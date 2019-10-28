import numpy as np
import os
import h5py
import datetime
import logging

logging.basicConfig(
    filename="logs/backup.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)


class BackUp:
    today = datetime.date.today()
    yesterday = datetime.date.today()-datetime.timedelta(1)

    dataset_pointer = 0

    def __init__(self, path, fname, ndim, attrs, sample_rate=1):
        dirname = os.path.dirname(__file__)
        self.storage_site = os.path.join(dirname, path)
        self.fname = fname

        # this is a guess of how many elements we should expect in a day
        self.est_samples = sample_rate * 60 * 60 * 24  # 1 sample per sample_rate

        # create handler to hd5 file, defaults to mode 'a'
        self.f = h5py.File(
            "{}/{}.hd5".format(self.storage_site, self.fname), "a")
        self.ndim = ndim
        self.attrs = attrs

        # create dataset for today if it doesn't exist
        self.create_dataset(ndim=self.ndim, attrs=self.attrs)

    def _get_today(self):
        return "{}-{}-{}".format(self.today.month, self.today.day, self.today.year)

    def _update_today(self):
        if (self.today - self.yesterday).days > 1:
            # update things for a new day
            self.today = datetime.date.today()
            self.yesterday = self.today - datetime.timedelta(1)

            # create new dataset
            self.create_dataset(ndim=self.ndim, attrs=self.attrs)

            # reset dataset pointer
            self.dataset_pointer = 0

    def update(self, data, size_increase_size=1000, tries=0):
        assert data.shape == (
            1, self.ndim), "incoming data not correct shape: {}".format(data.shape)

        try:
            # first get applicable dataset from file
            self._update_today()
            today = self._get_today()

            # update actual dataset with data
            dset = self.f[today]
            dset[self.dataset_pointer, :] = data
            self.dataset_pointer += 1

        except ValueError:
            logging.warning(
                "Reached the end of the allocated array size, attempting to resize...")
            if tries == 4:
                # if for some reason this function has been called 4 times in an attempt to resize array, it will exit
                logging.error(
                    "Max amount of recursion tries reached when calling to resize array")
                raise RecursionError(
                    "Max amount of recursion tries reached, array is not resizing properly.")

            # we have reached the end of our allocated size, resize array by n chunks
            current_size = dset.shape[0]
            dset.resize((current_size+size_increase_size, self.ndim))

            # recursive call this function so we don't lose the data that was tried to be appended
            self.update(
                data=data, size_increase_size=size_increase_size, tries=tries+1)

    def create_dataset(self, ndim, attrs=None):
        # creates a dataset with label of today's current date in Month/Day/Year format
        # dataset has ability to scale indefinitly, but ndim must be supplied
        # this function does nothing if the dataset already exists

        today = self._get_today()

        try:
            self.f.create_dataset(today, (self.est_samples, ndim), maxshape=(
                None, ndim), dtype=np.float32, chunks=True)
            if attrs is not None:
                assert isinstance(
                    attrs, dict), "supplied attributes must be in dictionary format"

                for key, value in attrs.items():
                    self.f[today].attrs[key] = value

        except RuntimeError:
            logging.warning(
                "dataset [{}] in [{}].hd5 already exists".format(today, self.fname))

    def get_dataset(self, dset_name):
        return self.f[dset_name]


if __name__ == "__main__":

    backup_settings = {
        'ndim': 5,
        'attrs': {
            'legend': "x,y,z,m,t"
        }
    }

    bup = BackUp(path="./example_backups",
                 fname="magnetometer", **backup_settings)

    for _ in range(bup.est_samples+1):

        x = np.random.randn(1, 5)
        bup.update(data=x)
