from app import get_torrent_list,delete_file,get_webdl_list,identify_stalled_files
import json


fullList = [*get_torrent_list(),*get_webdl_list()]

stalledFiles = identify_stalled_files(fullList)


# debugging
with open('full_list_tmp.json', 'w') as f:
    json.dump(fullList, f, indent=4)

with open('stalled_files_tmp.json', 'w') as f:
    json.dump(stalledFiles, f, indent=4)


print(stalledFiles,'stalledFiles')
for i,file in enumerate(stalledFiles):
    print(f"{i+1}/{len(stalledFiles)}",file['id'],'deleting...')
    delete_file(file['id'],file['type'])

print("All files deleted")
