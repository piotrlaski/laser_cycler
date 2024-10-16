import os

def get_file_creation_time(file_path:os.PathLike) -> float:

    file_metadata = os.stat(file_path)
    file_ctime = file_metadata.st_ctime
    return (file_ctime)

def get_last_created_dir_in_parent_dir(parent_dir_path:os.PathLike) -> os.PathLike:
    
    #init thresholds
    highest_ctime = float(0)
    newest_dir = str(0)
    
    for dir in os.listdir(parent_dir_path):
        rooted_dir = os.path.join(parent_dir_path, dir)
        rooted_dir_ctime = get_file_creation_time(rooted_dir)
        if rooted_dir_ctime > highest_ctime:
            newest_dir = rooted_dir
            highest_ctime = rooted_dir_ctime

    return (newest_dir)

def get_m06_content(file_path:os.PathLike) -> str:
    with open(file_path, 'r') as f:
        file_content = f.read()
    return file_content

def get_m06_file_path_in_parent_dir(parent_dir_path:os.PathLike) -> os.PathLike:
    for dir in os.listdir(parent_dir_path):
        if dir[-4:] == '.m06':
            rooted_m06_file = (os.path.join(parent_dir_path, dir))
            return rooted_m06_file        

def find_R_data_block(m06_content:str) -> str:

    ind_start = m06_content.rindex(r'no.set')
    ind_end = m06_content.rindex(r'R=sum')

    R_data_block = m06_content[ind_start:ind_end]
    R_data_block = R_data_block.splitlines()

    #remove header and trailer lines
    R_data_block = R_data_block[1:-2]

    return R_data_block

def calculate_R_factor(R_datablock:str) -> float:
    nominator = 0   #sum of abs (Robs - Rcalc)
    denominator = 0 #sum of Robs

    for line in R_datablock:
        line = line.split()
        eta = float(line[5])
        etac = float(line[6])
        R = eta + 1
        Rc = etac + 1
        nominator += abs(R - Rc)
        denominator += R

    R_factor = nominator / denominator
    return (R_factor)

def get_final_R_factor(refinement_directory:os.PathLike) -> float:

    lastdir =  get_last_created_dir_in_parent_dir(refinement_directory)
    m06_file = get_m06_file_path_in_parent_dir(lastdir)
    content = get_m06_content(m06_file)
    R_block = find_R_data_block(content)
    R_factor = calculate_R_factor(R_block)

    return (R_factor)

if __name__ == '__main__':

    FILES_PATH = r"C:\Users\piotr\Documents\VS_Code\working_dirs\cudppe_ref\all_Results\CuDPPE_g4_layer_percentage"

    for dir in os.listdir(FILES_PATH):
        if dir[-3:] != 'run':
            continue
        rooted_dir = os.path.join(FILES_PATH, dir)
        run_name = os.path.split(rooted_dir)[1]
        R_factor = get_final_R_factor(rooted_dir)
        print (f'{run_name} {R_factor}')