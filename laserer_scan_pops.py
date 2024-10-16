from main import *

def load_m41_file(m41_file_path: os.PathLike) -> str:
    with open(m41_file_path, 'r') as f:
        return f.read()

def modify_m41_text(m41_text: str, target_pop: str, double_molecule: bool = False) -> str:
    inject_string = f' {target_pop} {target_pop} {target_pop} {target_pop} {target_pop} {target_pop}      '
    m41_lines = m41_text.split('\n')
    m41_lines[2] = inject_string + m41_lines[2][-6:]  # leaving the population refinement switches intact
    if double_molecule:
        m41_lines[6] = inject_string + m41_lines[6][-6:]
    m41_text = '\n'.join(m41_lines)
    return m41_text

def save_m41_file(m41_text: str, target_file_path: os.PathLike, create_directory: bool = True) -> None:
    target_dir_path = os.path.split(target_file_path)[0]
    if create_directory and not os.path.isdir(target_dir_path):
        os.makedirs(target_dir_path)
    with open(target_file_path, 'w+') as f:
        f.write(m41_text)
    return

def prepare_directory(parent_ref_dir_path:os.PathLike, template_path: os.PathLike, target_pop: str, mol_name: str, double_molecule: bool = False) -> os.PathLike:

    ref_dir_name = str(float(target_pop) * 100)
    ref_dir_path = os.path.join(parent_ref_dir_path, ref_dir_name)
    try: os.makedirs(ref_dir_path)
    except FileExistsError: print(f'P{ref_dir_path} already exists') 

    #create the entire init directory needed for the refinement
    init_dir_path = os.path.join(ref_dir_path, 'init')
    copytree(template_path, init_dir_path, dirs_exist_ok=True)

    #take care of .m41 file, which is the only one that needs to be adjusted for new pops
    m41_path = os.path.join(init_dir_path, f'{mol_name}.m41')
    m41_text = load_m41_file(m41_path)
    modified_m41_text = modify_m41_text(m41_text, target_pop, double_molecule)
    save_m41_file(m41_text = modified_m41_text, target_file_path = m41_path)

    return ref_dir_path

def run_percentage_refs(parent_ref_dir_path:os.PathLike, template_path: os.PathLike, mol_name: str, nb_cycles: int, populations_list: list[float], double_molecule: bool = False) -> None:
    for population in populations_list:
        target_pop = f'{population/100:.6f}'
        ref_dir_path = prepare_directory(parent_ref_dir_path = parent_ref_dir_path,
                  template_path = template_path,
                  target_pop = target_pop,
                  mol_name = mol_name,
                  double_molecule = double_molecule)
        run_all(outputdir = ref_dir_path,
                name = mol_name,
                n = nb_cycles) 


if __name__ == '__main__':
    PERCENT_VALS = [0.5, 1.0, 1.5]
    #path containing 4 required files: *.m40, *.m41, *.m50 and *.m91, where *.m41 file can have anything as the starting population value 
    TEMPLATES_PATH = r'C:\Users\piotr\Documents\VS_Code\working_dirs\cudppe_ref\all_Results\multipercent\init'
    #are there two separate populations
    DOUBLE_MOLECULE = True 
    NB_CYCLES = 3
    #name of all the files, eg. MOLECULE_NAME.m41 etc...
    MOLECULE_NAME = 'cudppe'
    OUTPUT_PATH = r'C:\Users\piotr\Documents\VS_Code\working_dirs\cudppe_ref\all_Results\multipercent\test'

    run_percentage_refs(parent_ref_dir_path = OUTPUT_PATH,
                        template_path = TEMPLATES_PATH,
                        mol_name = MOLECULE_NAME,
                        nb_cycles= NB_CYCLES,
                        populations_list = PERCENT_VALS,
                        double_molecule = DOUBLE_MOLECULE)