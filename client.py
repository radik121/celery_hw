import requests

res = requests.post(
    'http://127.0.0.1:5000/advert/',
    json={'name': 'advert_3',
          'description': 'description_3',
          'owner_name': 'owner_3',
          "email": 'masagytov@image-line.ru'}
)
print(res.text)


# res = requests.get(
#     'http://127.0.0.1:5000/advert/0')
# print(res.text)


# res = requests.put(
#     'http://127.0.0.1:5000/advert/3',
#     json={'name': 'advert_5',
#           'description': 'description_5',
#           'owner_name': 'owner_2'}
# )
# print(res.text)

# res = requests.delete(
#     'http://127.0.0.1:5000/advert/5')
# print(res.text)
