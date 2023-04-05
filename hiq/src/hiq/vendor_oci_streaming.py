# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import oci

from base64 import b64encode
from hiq.utils import Singleton
import os


class OciStreamingClient(metaclass=Singleton):
    def __init__(
        self,
        ociMessageEndpoint=None,
        ociStreamOcid=None,
        ociConfigFilePath="~/.oci/config",
        ociProfileName="DEFAULT",
    ):
        if ociMessageEndpoint is None:
            ociMessageEndpoint = os.environ.get("OCI_STM_END", "")
        if ociStreamOcid is None:
            ociStreamOcid = os.environ.get("OCI_STM_OCID", "")
        if not ociMessageEndpoint:
            raise ValueError("🦉 Please setup environment variable `OCI_STM_END`")
        if not ociStreamOcid:
            raise ValueError("🦉 Please setup environment variable `OCI_STM_OCID`")
        self.ociMessageEndpoint = ociMessageEndpoint
        self.ociStreamOcid = ociStreamOcid
        self.ociConfigFilePath = ociConfigFilePath
        self.ociProfileName = ociProfileName

        self.config = oci.config.from_file(self.ociConfigFilePath, self.ociProfileName)
        self.client = oci.streaming.StreamClient(
            self.config, service_endpoint=ociMessageEndpoint
        )

    def __create_message(self, key, message):
        encoded_key = b64encode(key.encode()).decode()
        encoded_value = b64encode(message.encode()).decode()
        return [
            oci.streaming.models.PutMessagesDetailsEntry(
                key=encoded_key, value=encoded_value
            )
        ]

    def produce_messages(self, key, message, check=False):
        """produce message to OCI streaming

        Emits messages to a stream. There's no limit to the number of messages in a request, but the total size of a message or request must be 1 MiB or less. The service calculates the partition ID from the message key and stores messages that share a key on the same partition. If a message does not contain a key or if the key is null, the service generates a message key for you. The partition ID cannot be passed as a parameter.

        Args:
            key (str): message key
            message (str): message value
            check (bool, optional): if True, check the response from OCI streaming server. Defaults to False.
        """
        message_list = self.__create_message(key, message)
        messages = oci.streaming.models.PutMessagesDetails(messages=message_list)
        put_message_result = self.client.put_messages(self.ociStreamOcid, messages)

        if check:
            for entry in put_message_result.data.entries:
                if entry.error:
                    print("Error ({}) : {}".format(entry.error, entry.error_message))
                else:
                    print(
                        "Published message to partition {} , offset {}".format(
                            entry.partition, entry.offset
                        )
                    )


if __name__ == "__main__":
    client = OciStreamingClient()
    import time

    start = time.monotonic()
    client.produce_messages("hiq", "v2main,[🍁 n=fruit,s=0.00,e=40.00,x=0,c=0]")
    end = time.monotonic()
    # 1396091.409958899 super slow
    print((end - start) * 1e6)
