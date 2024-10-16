import os
import subprocess
from shutil import copytree

def load_m41_file(m41_file_path: os.PathLike) -> str:
    with open(m41_file_path, 'r') as f:
        return f.read()

def save_m41_file(m41_text: str, target_file_path: os.PathLike, create_directory: bool = True) -> None:
    target_dir_path = os.path.split(target_file_path)[0]
    if create_directory and not os.path.isdir(target_dir_path):
        os.makedirs(target_dir_path)
    with open(target_file_path, 'w') as f:
        f.write(m41_text)
    return

def switch_refinement(targeted_m41_text: str, goal_parameter: str, state: str) -> str:

    if state == 'on':
        sw = '1'
    elif state == 'off':
        sw = '0'

    m41_lines = targeted_m41_text.split('\n')

    if goal_parameter[:3] == 'pop':
        dataset_number = int(goal_parameter[-2])
        if goal_parameter[-1] == 'a':
            # padding is needed to prevent overflow when the last char change is requested:
            padded_m41_line = m41_lines[2] + ' '
            padded_m41_line_modified = padded_m41_line[:-8 + dataset_number] + sw + padded_m41_line[-7 + dataset_number:]
            m41_lines[2] = padded_m41_line_modified[:-1]
        else:
            padded_m41_line = m41_lines[6] + ' '
            padded_m41_line_modified = padded_m41_line[:-8 + dataset_number] + sw + padded_m41_line[-7 + dataset_number:]
            m41_lines[6] = padded_m41_line_modified[:-1]

    elif goal_parameter[:4] == 'temp':
        dataset_number = int(goal_parameter[-1])
        padded_m41_line = m41_lines[3] + ' '
        padded_m41_line_modified = padded_m41_line[:-8 + dataset_number] + sw + padded_m41_line[-7 + dataset_number:]
        m41_lines[3] = padded_m41_line_modified[:-1]

    elif goal_parameter[:2] == 'RG':
        param_length = len(goal_parameter + 'E')
        for i, elem in enumerate(m41_lines):
            if elem[:param_length] == goal_parameter + 'E':
                break
        # get the number of atoms present in the RG to skip to the end of RG section:
        nb_atoms = m41_lines[i].split()[1]
        target_line_nb = i + int(nb_atoms)*2 + 1
        m41_lines[target_line_nb] = m41_lines[target_line_nb][:-6] + f'{sw}{sw}{sw}' + m41_lines[target_line_nb][-3:]

    else:
        param_length = len(goal_parameter + 'E')
        for i, elem in enumerate(m41_lines):
            if elem[:param_length] == goal_parameter + 'E':
                break 
        m41_lines[i+1] = m41_lines[i+1][:-10] + f'0{sw}{sw}{sw}000000'

    modified_m41_text = '\n'.join(m41_lines)
    return modified_m41_text

def refine(templates_path: os.PathLike, output_path: os.PathLike, parameter_cycle: list[list[str]], nb_cycles: int) -> None:
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    init_path = os.path.join(output_path, 'init')
    copytree(templates_path, init_path)
    last_iter_path = os.path.join(output_path, 'last_iter')
    copytree(templates_path, last_iter_path)

    #get the name of the molecule/file, as LASER needs it explicitly (assume that all non-exe files are named the same as .m41)
    mol_name = [name[:-4] for name in os.listdir(init_path) if name[-4:] == '.m41'][0]

    for i in range(nb_cycles):
        for j, parameter_list in enumerate(parameter_cycle):
            cur_cycle_name = f'Cycle{i+1}_{j+1}'
            cur_dir_path = os.path.join(output_path, cur_cycle_name)
            copytree(last_iter_path, cur_dir_path)
            
            ## import m41 to memory
            m41_text = load_m41_file(os.path.join(cur_dir_path, f'{mol_name}.m41'))
            
            ## turn params on
            for param in parameter_list:
                m41_text = switch_refinement(m41_text, param, state='on')
            
            ## save m41 to curdir
            save_m41_file(m41_text, os.path.join(cur_dir_path, f'{mol_name}.m41'))
            
            ## temporarly change cwd and refine (LASER requires running from current directory)
            laser_exec_path = os.path.join(cur_dir_path,'laserO3win32.exe')
            cwd = os.getcwd()
            os.chdir(cur_dir_path)
            subprocess.run([laser_exec_path], input=f'0\n{mol_name}', text=True)
            os.chdir(cwd)

            ## load m41 back to memory and turn off params
            m41_text = load_m41_file(os.path.join(cur_dir_path, f'{mol_name}.m41'))
            for param in parameter_list:
                m41_text = switch_refinement(m41_text, param, state='off')

            ## save m41 to lastiter
            save_m41_file(m41_text, os.path.join(last_iter_path, f'{mol_name}.m41'))
    return

if __name__ == '__main__':

    #       User notes:
    #
    #       Regarding path variables:
    #   Make sure that the path variables OUTPUT_PATH and TEMPLATE_PATH have the 'r' letter before the first quotation mark (e.g. r"C:\Users\piotr\Desktop")
    #   The template path folder should contain: "molecle.m40", "molecule.m41", "molecule.m91", "molecule.m50" and "laserO3win32.exe". ("molecule" can be any name, just has to be the same for all files)
    #   The output path doesn't have to exist beforehand
    #
    #       Regarding GOAL_PARAMS list configuration:
    #   Cu1 means enable Cu1E translation. Same goes for any other atom/anchor
    #   RG1 means ONLY rotations for rigid body named RG1E. If you want translations, you have to write the anchor atom name (see above)
    #   pop1a means population from 1st dataset for molecule 1. pop1b means population from 1st dataset for molecule 2. pop3a means population from 3rd dataset for molecule 1 etc...
    #   temp1 means temperature scale factor for 1st set
    #   
    #   In order to refine two things at once, place them in a nested list next to each other:  ['N1', 'RG1']


    OUTPUT_PATH = r"C:\Users\piotr\Documents\VS_Code\working_dirs\cudppe_ref\all_Results\anc_CuDPPE_g4_layer_newrigids\att2"
    TEMPLATES_PATH = r"C:\Users\piotr\Documents\VS_Code\working_dirs\cudppe_ref\all_Results\anc_CuDPPE_g4_layer_newrigids\init"
    NB_CYCLES = 20
    GOAL_PARAMS = [['Cu1'],
                   ['N1','RG1'],
                   ['P1','RG2'],
                   ['pop1a','temp1'],
                   ['Cu2'],
                   ['N1a','RG4'],
                   ['P3','RG5'],
                   ['pop1b','temp1']]


    refine(templates_path=TEMPLATES_PATH,
           output_path=OUTPUT_PATH,
           parameter_cycle=GOAL_PARAMS,
           nb_cycles=NB_CYCLES)
    