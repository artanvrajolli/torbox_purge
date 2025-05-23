from app import get_torrent_list,delete_file,get_webdl_list,identify_stalled_files



stalledFiles = identify_stalled_files([*get_torrent_list(),*get_webdl_list()])

print(stalledFiles,'stalledFiles')
for i,file in enumerate(stalledFiles):
    print(f"{i+1}/{len(stalledFiles)}",file['id'],'deleting...')
    delete_file(file['id'],file['type'])

print("All files deleted")
