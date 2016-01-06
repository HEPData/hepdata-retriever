from urllib2 import HTTPError
import zipfile
import os
import shutil
import yaml
from yaml.scanner import ScannerError
import logging

__author__ = 'eamonnmaguire'

logging.basicConfig()
log = logging.getLogger(__name__)


class Retriever(object):
    """
    """

    def __init__(self, output_directory,
                 base_url="http://hepdata.cedar.ac.uk/view/{0}/yaml"):
        self.base_url = base_url
        self.output_directory = output_directory

    def get_record(self, inspire_id):

        file_location = self.download_file(inspire_id)
        if file_location:
            # create a dictionary that contains references to a submission
            # yaml, and N data files.
            self.split_files(file_location,
                             os.path.join(self.output_directory, inspire_id),
                             os.path.join(self.output_directory,
                                          inspire_id + ".zip"))

            os.remove(file_location)

        else:
            log.error('Failed to load ' + inspire_id)

    def download_file(self, inspire_id):
        """
        :param inspire_id:
        :return:
        """
        import urllib2
        import tempfile

        try:
            response = urllib2.urlopen(self.base_url.format(inspire_id))
            yaml = response.read()
            # save to tmp file

            tmp_file = tempfile.NamedTemporaryFile(dir=self.output_directory,
                                                   delete=False)
            tmp_file.write(yaml)
            tmp_file.close()
            return tmp_file.name

        except HTTPError as e:
            log.error('Failed to download {0}'.format(inspire_id))
            log.error(e.message)
            return None

    def write_submission_yaml_block(self, document, submission_yaml,
                                    type="info"):
        submission_yaml.write("---\n")
        self.cleanup_yaml(document, type)
        yaml.dump(document, submission_yaml, allow_unicode=True)
        submission_yaml.write("\n")

    def split_files(self, file_location, output_location,
                    archive_location=None):
        """
        :param file_location:
        :param output_location:
        :param archive_location:
        :return:
        """
        try:
            file_documents = yaml.load_all(open(file_location, 'r'))

            # make a submission directory where all the files will be stored.
            # delete a directory in the event that it exists.
            if os.path.exists(output_location):
                shutil.rmtree(output_location)

            os.makedirs(output_location)

            with open(os.path.join(output_location, "submission.yaml"),
                      'w') as submission_yaml:
                for document in file_documents:
                    if "record_ids" in document:
                        self.write_submission_yaml_block(document,
                                                         submission_yaml)

                    else:
                        file_name = document["name"].replace(' ', '') + ".yaml"
                        document["data_file"] = file_name

                        with open(os.path.join(output_location, file_name),
                                  'w') as data_file:
                            yaml.dump(
                                {"independent_variables":
                                    self.cleanup_data_yaml(
                                        document["independent_variables"]),
                                    "dependent_variables":
                                        self.cleanup_data_yaml(
                                            document["dependent_variables"])},
                                data_file, allow_unicode=True)

                        self.write_submission_yaml_block(document,
                                                         submission_yaml,
                                                         type="record")

            if archive_location:
                if os.path.exists(archive_location):
                    os.remove(archive_location)

                zipf = zipfile.ZipFile(archive_location, 'w')
                os.chdir(output_location)
                self.zipdir(".", zipf)
                zipf.close()
        except ScannerError as se:

            log.error(
                'Error parsing {0}, {1}'.format(file_location, se.message))
            raise se

    def cleanup_data_yaml(self, yaml):
        """
        Casts strings to numbers where possible, e.g
        :param yaml:
        :return:
        """
        if yaml is None:
            yaml = []

        self.convert_string_to_numbers(yaml)

        return yaml

    def convert_string_to_numbers(self, variable_set):
        fields = ["value", "high", "low"]

        if variable_set is not None:
            for variable in variable_set:
                if type(variable) is dict:
                    if variable["values"] is not None:
                        for value_item in variable["values"]:
                            try:
                                for field in fields:
                                    if field in value_item:
                                        value_item[field] = float(
                                            value_item[field])
                            except ValueError:
                                pass
                    else:
                        variable["values"] = []
        else:
            variable_set = []

    def cleanup_yaml(self, yaml, type):
        keys_to_remove = ["dateupdated",
                          "independent_variables",
                          "dependent_variables"]
        self.remove_keys(yaml, keys_to_remove)

        if type is 'info':
            self.add_field_if_needed(yaml, 'comment',
                                     'No description provided.')
        else:
            self.add_field_if_needed(yaml, 'keywords', [])
            self.add_field_if_needed(yaml, 'description',
                                     'No description provided.')

        if "label" in yaml:
            yaml["location"] = yaml["label"]
            del yaml["label"]

    def add_field_if_needed(self, yaml, field_name, default_value):
        if not (field_name in yaml):
            yaml[field_name] = default_value

    def remove_keys(self, yaml, to_remove):
        """
        :param yaml:
        :return:
        """
        for key in yaml:
            if not yaml[key]:
                to_remove.append(key)

        for key in to_remove:
            if key in yaml:
                del yaml[key]

    def zipdir(self, path, ziph):
        """
        From http://stackoverflow.com/questions/1855095/how-to-create-a-zip-
        archive-of-a-directory?answertab=active#tab-top
        :param path:
        :param ziph:
        :return:
        """
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    def get_all_ids_in_current_system(self, year=None,
                                      prepender_id_with="ins"):
        import requests, re

        brackets_re = re.compile(r'\[+|\]+')
        inspire_ids = []
        base_url = 'http://hepdata.cedar.ac.uk/allids/{0}'
        if year:
            base_url = base_url.format(year)
        else:
            base_url = base_url.format('')
        response = requests.get(base_url)
        if response.ok:
            _all_ids = response.text
            for match in re.finditer('\[[0-9]+,[0-9]+,[0-9]+\]', _all_ids):
                start = match.start()
                end = match.end()
                # process the block which is of the form [inspire_id,xxx,xxx]
                id_block = brackets_re.sub("", _all_ids[start:end])
                id = id_block.split(',')[0].strip()
                if id != '0': inspire_ids.append(
                    prepender_id_with + "{}".format(id))
        return inspire_ids
