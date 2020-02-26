VGG Text Search - Test
=======================

Author:

 + Ernesto Coto, University of Oxford - <ecoto@robots.ox.ac.uk>

Overview
--------

The scripts in this folder are created to test the VGG Text Search service. One script tests the service independently of any frontend, and the other simulates the communication with the [vgg_frontend](https://gitlab.com/vgg/vgg_frontend). However, **these scripts can also be seen as an example of usage of the VGG Text Search service**, in case you want to develop your own web frontend to replace the [vgg_frontend](https://gitlab.com/vgg/vgg_frontend).

#### *Testing the service without a frontend*

By using the `test_retrieval_class.py` you can run a simple query over the text-index using the TextRetrieval class. In a separate window, execute:

```
python test_retrieval_class.py <query_string>
```

where `<query_string>` corresponds to the input word for your search. Make sure `<query_string>` is just one word and does not contain special characters.

The script will run the search without the need of any network communication and print the results in the terminal window.


#### *Testing the service with a frontend*


By using the `test_retrieval_service.py` you can run a simple query over the text-index but using sockets to communicate with the TextRetrieval class. First, you will need to start the VGG Text Search service as indicated in the [Usage](https://gitlab.com/vgg/vgg_text_search#usage). Then, once the service is running, execute in a separate window: 

```
python test_retrieval_service.py <query_string>
```

where `<query_string>` corresponds to the input word for your search. Make sure `<query_string>` is just one word and does not contain special characters.

The script will communicate with the VGG Text Search simulating the [vgg_frontend](https://gitlab.com/vgg/vgg_frontend), run your search and then print the results in the terminal window.


