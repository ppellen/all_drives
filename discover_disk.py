
import subprocess, json

def discover_disk():
    result = subprocess.run(
        ['lsblk',  '--json'],
        stdout = subprocess.PIPE,
        universal_newlines = True # Python >= 3.7 also accepts "text=True"
    )
    #  print(result.stdout)  # a lot of json
    donnees = json.loads(result.stdout)
    blockdevices = donnees['blockdevices']

    external_disk_name = \
        this_mountpoint = \
        repertoire = None

    for blockdevice in blockdevices:
        if "sdb" == blockdevice['name']:
            for child in blockdevice['children']:
                # print(child['name'])

                for mountpoint in child['mountpoints']:
                    external_disk_name = mountpoint.split('/')[-1]
                    this_mountpoint = mountpoint
                    break
            # print('------')

    return external_disk_name, this_mountpoint

if __name__ == '__main__':
    external_disk_name, mountpoint = discover_disk()
    print(external_disk_name, mountpoint )