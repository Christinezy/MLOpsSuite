import fsspec
from pathlib import Path

def get_code(url_metadata, personal_github_id,gittoken,project_id,version_number):
    
    # loc = Path() / ".." / 'services' /"user_models" / f"Project_{project_id}" / f"Version_{version_number}"
    #loc = Path() / ".." / 'services' /"mlops_files" / f"Project_{project_id}" / f"Version_{version_number}"
    loc = Path() / ".." / 'services' /"mlops_files" / f"project_{project_id}" / f"version_{version_number}"
    #print(loc)
    loc.mkdir(exist_ok=True, parents=True)

    project_github_id,github_project_name  = (url_metadata[3],url_metadata[4])

    if url_metadata[-1] != '': # Files
        folder_loc,file_name = ('/'.join(url_metadata[7:-1]),url_metadata[-1])
        dest = loc / file_name
        fs = fsspec.filesystem('github', org=project_github_id,
                            repo=github_project_name, username=personal_github_id, token=gittoken)
        fs.get('/'.join([folder_loc, file_name]), dest.as_posix())

    elif url_metadata[-1] == '': # Folder
        folder_loc = '/'.join(url_metadata[7:])
        fs = fsspec.filesystem('github', org=project_github_id,
                            repo=github_project_name, username=personal_github_id, token=gittoken)
        fs.get(folder_loc + "/", loc.as_posix(), recursive=True)
    else:
        print("Wrong URL format") 
        return False
    return True