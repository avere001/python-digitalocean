from typing import Union, List

from digitalocean.Volume import Volume
from .baseapi import BaseAPI


class Tag(BaseAPI):
    def __init__(self, *args, **kwargs):
        self.name = ""
        self.resources = {}
        super(Tag, self).__init__(*args, **kwargs)

    @classmethod
    def get_object(cls, api_token, tag_name):
        tag = cls(token=api_token, name=tag_name)
        tag.load()
        return tag

    def load(self):
        """
           Fetch data about tag
        """
        tags = self.get_data("tags/%s" % self.name)
        tag = tags['tag']

        for attr in tag.keys():
            setattr(self, attr, tag[attr])

        return self

    def create(self, **kwargs):
        """
            Create the tag.
        """
        for attr in kwargs.keys():
            setattr(self, attr, kwargs[attr])

        params = {"name": self.name}

        output = self.get_data("tags", type="POST", params=params)
        if output:
            self.name = output['tag']['name']
            self.resources = output['tag']['resources']

    def delete(self):
        return self.get_data("tags/%s" % self.name, type="DELETE")

    def __get_resources(self, resources, method):

        """ Method used to talk directly to the API (TAGs' Resources) """
        tagged = self.get_data(
            'tags/%s/resources' % self.name, params={
                "resources": resources
            },
            type=method,
        )
        return tagged

    def __add_resources(self, resources):
        """
            Add the resources to this tag.

            Attributes accepted at creation time:
                resources: array - See API.
        """
        return self.__get_resources(resources, method='POST')

    def __remove_resources(self, resources):
        """
            Remove resources from this tag.

            Attributes accepted at creation time:
                resources: array - See API.
        """
        return self.__get_resources(resources, method='DELETE')

    def __build_resources_field(self, resources_to_tag, resource_type):
        """
            Private method to build the `resources` field used to tag/untag
            DO resources. Returns an array of objects containing two fields:
            resource_id and resource_type.
            It checks the type of objects in the 1st argument and build the
            right structure for the API. It accepts array of strings, array
            of ints and array of the object type defined by object_class arg.
            The 3rd argument specify the resource type as defined by DO API
            (like droplet, image, volume or volume_snapshot).
            See: https://developers.digitalocean.com/documentation/v2/#tag-a-resource
        """
        resources_field = []

        for resource_to_tag in resources_to_tag:
            resource_id = getattr(resources_to_tag, "id", resource_to_tag)
            if resource_id:
                resources_field.append({
                    "resource_type": resource_type,
                    "resource_id": str(resource_id)
                })

        return resources_field

    def add_volumes(self, volumes: List[Union[Volume, str]]):
        """
        Attach this tag to the given volumes.
        """
        return self.add_resources(volumes, 'volume')

    def remove_volumes(self, volumes: List[Union[Volume, str]]):
        """
        Remove this tag from the given volumes.
        """
        return self.remove_resources(volumes, 'volume')

    def add_droplets(self, droplets):
        """
            Add the Tag to a droplet or droplets.

            droplet: array of string or array of int, or array of Droplets.
        """
        return self.add_resources(droplets, 'droplet')

    def remove_droplets(self, droplets):
        """
            Remove the Tag from the droplet or droplets.

            droplet: array of string or array of int, or array of Droplets.
        """
        return self.remove_resources(droplets, 'droplet')

    def add_snapshots(self, snapshots):
        """
            Add the Tag to the Snapshot.

            Attributes accepted at creation time:
                snapshots: array of string or array of int or array of Snapshot.
        """
        return self.add_resources(snapshots, 'volume_snapshot')

    def remove_snapshots(self, snapshots):
        """
        remove the Tag from the Snapshot.

        snapshots: array of string or array of int or array of Snapshot.
        """
        return self.remove_resources(snapshots, 'volume_snapshot')

    def add_resources(self, resources, resource_type: str):
        """
        Add the Tag to a resource or resources.

        resources: array of string or array of int, or array of resources
                   of the specified resource type.
        resource_type_id: The type of resource (i.e. droplet, volume_snapshot, volume)
        """

        if not isinstance(resources, list):
            resources = [resources]

        # Extracting data from the Droplet object
        resource_fields = self.__build_resources_field(resources, resource_type)
        if len(resource_fields) > 0:
            return self.__add_resources(resource_fields)

        return False

    def remove_resources(self, resources, resource_type: str):
        """
        Remove the Tag from a resource or resources.

        resources: array of string or array of int, or array of resources
                   of the specified resource type.
        resource_type_id: The name of the resource type (i.e. droplet, volume_snapshot, volume)
        """

        if not isinstance(resources, list):
            resources = [resources]

        # Extracting data from the Droplet object
        resource_fields = self.__build_resources_field(resources, resource_type)
        if len(resource_fields) > 0:
            return self.__remove_resources(resource_fields)

        return False
