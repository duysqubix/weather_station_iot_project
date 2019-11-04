import numpy as np
import os
import h5py
import datetime
import logging

logging.basicConfig(filename="logs/backup.log",
                    level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s")


class BackUp:
    today = datetime.date.today()
    yesterday = datetime.date.today() - datetime.timedelta(1)

    dataset_pointer = 0

    def __init__(self, path, fname, **settings):
        dirname = os.path.dirname(__file__)
        self.storage_site = os.path.join(dirname, path)
        self.fname = fname

        # this is a guess of how many elements we should expect in a day
        self.est_samples = settings[
            'sample_rate'] * 60 * 60 * 24  # 1 sample per sample_rate

        # create handler to hd5 file, defaults to mode 'a'
        self.f = h5py.File("{}/{}.hd5".format(self.storage_site, self.fname),
                           "a")
        self.ndim = settings['ndim']
        self.attrs = settings['attrs']
        self.batch_size = settings['batch_size']

        # create dataset for today if it doesn't exist
        self.create_dataset(ndim=self.ndim, attrs=self.attrs)

    def _get_today(self):
        return "{}-{}-{}".format(self.today.month, self.today.day,
                                 self.today.year)

    def _trim_dataset(self, dset=None):
        dset = self.f[self._get_today()] if dset is None else dset

        last_non_zero_idx = np.nonzero(dset[()])[0][-1]
        dset.resize((last_non_zero_idx, self.ndim))

    def _update_today(self):
        if (self.today - self.yesterday).days > 1:
            # update things for a new day
            self.today = datetime.date.today()
            self.yesterday = self.today - datetime.timedelta(1)

            # before creating new dataset, trim current dataset so that any hanging zeros are removed. This will optimize space efficiency as well
            dset = self.f[self._get_today()]
            self._trim_dataset(dset=dset)

            # create new dataset
            self.create_dataset(ndim=self.ndim, attrs=self.attrs)

            # reset dataset pointer
            self.dataset_pointer = 0

    def update(self, data, size_increase_size=None, tries=0):
        assert data.shape == (
            self.batch_size,
            self.ndim), "incoming data not correct shape: {}".format(
                data.shape)

        size_increase_size = self.est_samples if size_increase_size is None else size_increase_size

        try:
            # first get applicable dataset from file
            self._update_today()
            today = self._get_today()

            print("dshape: {} {}:{}\t->\t".format(
                data.shape, self.dataset_pointer,
                self.dataset_pointer + self.batch_size),
                  end='')
            # update actual dataset with data
            dset = self.f[today]
            dset[self.dataset_pointer:self.dataset_pointer +
                 self.batch_size, :] = data
            self.dataset_pointer += self.batch_size
            print("{}:{}".format(self.dataset_pointer,
                                 self.dataset_pointer + self.batch_size))

        except (ValueError, TypeError) as e:
            # this will most likely fire when allocated array is fully full and attempting to access idx that is beyond the limitations of the array alloted.
            logging.warning(e)
            logging.warning(
                "Reached the end of the allocated array size, attempting to resize..."
            )

            if tries == 4:
                # if for some reason this function has been called 4 times in an attempt to resize array, it will exit
                logging.error(
                    "Max amount of recursion tries reached when calling to resize array"
                )
                raise RecursionError(
                    "Max amount of recursion tries reached, array is not resizing properly."
                )

            # we have reached the end of our allocated size, resize array by n chunks
            current_size = dset.shape[0]
            dset.resize((current_size + size_increase_size, self.ndim))
            logging.info(
                "Successfully resized array with new dimensions: {}".format(
                    dset.shape))

            # recursive call this function so we don't lose the data that was tried to be appended
            logging.info(
                "Attempting to update dataset with newly allocated array size, try [{}]"
                .format(tries))
            self.update(data=data,
                        size_increase_size=size_increase_size,
                        tries=tries + 1)

    def create_dataset(self, ndim, attrs=None):
        # creates a dataset with label of today's current date in Month/Day/Year format
        # dataset has ability to scale indefinitly, but ndim must be supplied
        # this function does nothing if the dataset already exists

        today = self._get_today()

        try:
            self.f.create_dataset(today, (self.est_samples, ndim),
                                  maxshape=(None, ndim),
                                  dtype=np.float32,
                                  chunks=True)
            if attrs is not None:
                assert isinstance(
                    attrs,
                    dict), "supplied attributes must be in dictionary format"

                for key, value in attrs.items():
                    self.f[today].attrs[key] = value

        except RuntimeError:
            logging.warning("dataset [{}] in [{}].hd5 already exists".format(
                today, self.fname))

    def get_dataset(self, dset_name):
        return self.f[dset_name]


if __name__ == "__main__":
    from iot_devices import Magnometer

    mag = Magnometer(topic=None, name='magnetometer')
    mag.device_setup()

    # this needs to simuate an array filling up from real data and then sending that chunk of data
    # through the update method

    buffer = np.zeros((mag.backup_h.batch_size, mag.backup_h.ndim))
    print(buffer.shape, mag.backup_h.est_samples, mag.backup_h.batch_size)

    # iterate through rounds of est_samples and batch_size
    for j in range(mag.backup_h.est_samples * 2 // mag.backup_h.batch_size):

        # iterate and fill batch_size empty array
        for i in range(mag.backup_h.batch_size):
            sample = np.arange(mag.backup_h.ndim) + (i * mag.backup_h.ndim)
            sample = sample.reshape(1, mag.backup_h.ndim)
            buffer[i, :] = sample

        # physically update hdf5 file once batch_size buffer has been filled.
        mag.backup_h.update(data=buffer)
        # print("Round ", j)

    # This section of code should execute when a new day arrives and new hdf5 file is created..

    # grab current data set
    dset = mag.backup_h.f[mag.backup_h._get_today()]

    # sanity check, shows length of allocated array
    print(len(dset[()]))

    # perform the trim
    mag.backup_h._trim_dataset(dset=None)

    # print length of trimed dataset
    print(len(dset[()]))
