#############################################
# View hdf5 files in an interactive session #
#############################################

import argparse
import h5py
import numpy as np


class HDFViewer:
    prompt = "> "
    cur_dir = '/'
    home_dir = '/'
    _main_loop = True

    def __init__(self, path):
        self.path = path
        self.f = h5py.File(path, 'r')

        self.cur_view = {
            'B': (self._do_back, None),
            'X': (self._do_exit, None)
        }

    def _reset_cur_view(self):
        self.cur_view = {
            'B': (self._do_back, None),
            'X': (self._do_exit, None)
        }

    def _display(self, hdf_path):
        print("\n" + hdf_path)
        hdf_path = self.f[hdf_path]
        display = ""

        if isinstance(hdf_path, h5py.Group):
            for i, (key, type_) in enumerate(hdf_path.items()):
                display += "({}) [{}]: {}\n".format(i, key, type_)
                self.cur_view[str(i)] = (self._do_options, [key, type_])

        elif isinstance(hdf_path, h5py.Dataset):
            display += str(hdf_path) + "\n"
            self.cur_view['V'] = (self._do_show_dataset_values, None)
            self.cur_view['E'] = (self._do_export, None)

            display += "(V) Values\n"
            display += "(E) Export\n"

        display += "(B) Back\n"
        display += "(X) Exit\n"
        print(display)

    def _parse(self):

        response = input(self.prompt)
        if response in self.cur_view.keys():
            rsp = self.cur_view[response]
            func, args = rsp[0], rsp[1]
            self.do(func, args)
        else:
            print("Not a valid option")

    def do(self, response, args):
        response(args)

    def _do_options(self, *args):
        key, _ = args[0]
        self.prompt = "[{}] > ".format(key)
        self.cur_dir += "/{}".format(key)

        print(*args)

    def _do_show_dataset_values(self, *args):
        dset = self.f[self.cur_dir]
        print(dset.value)
        self._wait()

    def _do_export(self, *args):
        dset = self.f[self.cur_dir]
        save_path = self.cur_dir.split('/')[-1]
        np.save(save_path + ".npy", dset.value)
        print("saved as binary numpy")
        self._wait()

    def _wait(self):
        input("Enter to continue")

    def _do_back(self, *args):
        if self.cur_dir != self.home_dir:
            new_dir = "/" + "/".join(self.cur_dir.split("/")[1:-1])
            self.cur_dir = new_dir

    def _do_exit(self, *args):
        print("Exitting")
        self._main_loop = False

    def loop(self):
        while self._main_loop:
            self._reset_cur_view()
            self._display(hdf_path=self.cur_dir)
            self._parse()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View hdf5 files")
    parser.add_argument('--path', type=str, help='path to the hdf5 file')
    args = vars(parser.parse_args())

    path = args['path']
    viewer = HDFViewer(path=path)
    viewer.loop()
