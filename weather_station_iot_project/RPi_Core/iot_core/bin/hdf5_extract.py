import argparse
import h5py
import numpy as np
import logging
from log import log


class HDF5Handler:
    def __init__(self, path, dsetname):
        self.path = path
        self.dsetname = dsetname

    def extract(self):
        while 1:
            try:
                with h5py.File(self.path, 'r') as f:
                    dset = f[self.dsetname][()]
                    attrs = dict(f[self.dsetname].attrs)
                    return dset, attrs
            except IOError as err:
                log(logging.info, msg=err)

    def apply_func(self, func, *args, **kwargs):
        while 1:
            try:
                with h5py.File(self.path, 'r') as f:
                    result = func(f, args, kwargs)
                    return result
            except IOError as err:
                log(logging.info, msg=err)


class Convert:
    output_type = str
    _convert_options = dict()

    def __init__(self, output_type):
        self.output_type = output_type
        self._convert_options = {
            'npy': self._npy,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def convert(self, data, name, output_path=None):
        output_path = "./" if output_path is None else output_path
        output_path += name
        self._convert_options[self.output_type](data=data, out=output_path)

    def _npy(self, data, out):
        out += ".npy"
        np.save(out, data)
        print("Saved: {}".format(out))


def extract_metadata(f, *args, **kwargs):
    file_contents = {}
    for name, dataset in f.items():
        file_contents[name] = {'data': dataset[()]}
        for attr_name, attr_value in dataset.attrs.items():
            file_contents[name][attr_name] = attr_value

    return file_contents


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract HDF5 Dataset and save as another format")
    parser.add_argument('-p', '--path', type=str, help='path to the hdf5 file')
    parser.add_argument('-d', '--dataset', type=str, help='name of dataset')
    parser.add_argument('-n',
                        '--outname',
                        type=str,
                        help='name of output file')

    parser.add_argument(
        '-f',
        '--outpath',
        type=str,
        help='output path, if left blank it will assume current working dir.')

    parser.add_argument('-t',
                        '--type',
                        type=str,
                        help='output format ',
                        choices=['npy', 'hdf5'])
    args = vars(parser.parse_args())

    if args['type'] == 'hdf5':

        # make a copy of file
        h = HDF5Handler(path=args['path'], dsetname=None)
        outpath = args['outpath'] if args['outpath'] is not None else "./"
        outpath = outpath + args['outname'] + ".hd5"
        with h5py.File(outpath, 'w') as copy:
            file_contents = h.apply_func(extract_metadata)

            # now that file_contents is stored in memory, copy over to new file and close
            for key, values in file_contents.items():
                dset = file_contents[key]['data']
                copy.create_dataset(name=key, data=dset)
                for attr_name, attr_val in values.items():
                    if attr_name == 'data':
                        continue
                    copy[key].attrs[attr_name] = attr_val
        print("Saved: {}".format(outpath))
    else:

        dset = HDF5Handler(path=args['path'],
                           dsetname=args['dataset']).extract()

        with Convert(output_type=args['type']) as convert:
            convert.convert(data=dset,
                            name=args['outname'],
                            output_path=args['outpath'])
