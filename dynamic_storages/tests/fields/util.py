from django.core.files import File


def open_file(file_path):
    ret_val = []
    ret_val.append(file_path.split("/")[-1])
    ret_val.append(File(open(file_path, "rb")))
    return ret_val
