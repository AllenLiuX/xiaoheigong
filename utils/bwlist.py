import pickle
import os
from definitions import ROOT_DIR
import pprint as pp


class BWList:
    """
    A data structure that stores blacklist/whitelisted pdf ids in self.list
    """
    def __init__(self, search_keyword, black_white):
        self.keyword = search_keyword

        if black_white == 'black':
            self.save_path = os.path.join(ROOT_DIR, 'cache', self.keyword, 'blacklist.pkl')
        elif black_white == 'white':
            self.save_path = os.path.join(ROOT_DIR, 'cache', self.keyword, 'whitelist.pkl')

        # Initializes/Loads list
        if self.bwlist_exist():
            self.list = self.load_bwlist()
        else:
            self.list = {}

    def bwlist_exist(self) -> bool:
        """
        Check if blacklist/whitelist already exist
        :return: True if already exist
        """
        return os.path.exists(self.save_path)

    def in_bwlist(self, doc_id, source) -> bool:
        """
        Helper method to check if a document is in blacklist/whitelist
        :param doc_id: the document id
        :param source: the website source ('fxbg', 'robo'...)
        :return: True if the blacklist/whitelist has the document
        """
        # Convert doc_id to string if it was int type
        if type(doc_id) == int:
            doc_id = str(doc_id)
        return source in self.list and doc_id in self.list[source]

    def load_bwlist(self) -> dict:
        """
        Loads blacklist/whitelist from directory to dict
        :return: the dict that stores the blacklisted/whitelisted pdfs
        """
        try:
            bwlist_file = open(self.save_path, 'rb')
            output = pickle.load(bwlist_file)
            return output
        except FileNotFoundError:
            print("BWList does not exist!")

    def save_bwlist(self):
        """
        Saves the blacklist/whitelist
        """
        with open(self.save_path, 'wb') as file:
            pickle.dump(self.list, file)
            file.close()

    def add_to_bwlist(self, source: str, doc_id: str):
        """
        Adds a document to blacklist/whitelist
        :param source: website that the doc is downloaded from
        :param doc_id: doc id
        """
        if source in self.list.keys():
            existing_ids = self.list[source]
            existing_ids.add(doc_id)
            self.list.update({source: existing_ids})
        else:
            new_ids = {doc_id}
            self.list.update({source: new_ids})

    def bwlist_filter(self, id_list, source):
        """
        Removes all ids in id_list
        :param id_list: the list of pdf ids that needs to be filtered
        :param source: the website where the pdfs are downloaded
        :return: the filtered pdf id list
        """
        result = None

        # If id_list is a list, return a list; if it's a dict, return a dict
        if type(id_list) == list:
            result = []
            for doc_id in id_list:
                if not self.in_bwlist(doc_id, source):
                    result.append(doc_id)
        elif type(id_list) == dict:
            result = id_list.copy()
            for doc_id in id_list:
                if self.in_bwlist(doc_id, source):
                    result.pop(doc_id)

        return result


if __name__ == '__main__':
    print("welcome")
