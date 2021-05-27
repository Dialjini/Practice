from app import models, db
import requests
import json

f = open('token_last_update.txt')
token = f.readline().replace('\n', '')
f.close()

headers = {
    'Content-Type': 'application/json'
}

def add_users():
    user1 = models.User()
    user2 = models.User()
    user1.name = 'Солдатов'
    user2.name = 'Кустов'
    user1.team_id = 1
    user2.team_id = 1
    user1.address = 'Берёзовая 228, кв 8'
    user2.address = 'Берёзовая 228, кв 9'
    user1.leader_status = False
    user2.leader_status = True
    user1.driver_status = False
    user2.driver_status = True
    user1.phone = '89009009000'
    user2.phone = '89132281337'
    user1.role = 'admin'
    user2.role = 'admin'
    user1.status = 'В пути'
    user2.status = 'Не на рабочем месте'
    user1.login = 'test'
    user1.password = 'test'
    user2.login = 'test1'
    user2.password = 'test1'
    user2.car_info = 'Мерседес S, А666АА'

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

def getContact(deal_id):
    url = 'https://crm.terrakultur.ru/rest/{0}?access_token={1}&id={2}'.format('crm.company.contact.items.get', token, deal_id)
    r = requests.get(url)
    result = []
    r = json.loads(r.content.decode('utf-8'))
    if 'error' not in r:
        for i in r['result']:
            url = 'https://crm.terrakultur.ru/rest/{0}?access_token={1}&id={2}'.format('crm.contact.get', token, i['CONTACT_ID'])
            req = requests.get(url)
            result.append(json.loads(req.content.decode('utf-8'))['result'])
    return result


def add_clients():
    client_info = []
    client_buffer = []

    method_folder = 'crm.deal.list'

    next = 0
    while True:
        filt = json.dumps({'filter': {'=TYPE_ID': 'SERVICE', '=CATEGORY_ID': '1'},
                           'select': ['COMPANY_ID', 'ID', 'UF_CRM_1593170402072', 'UF_CRM_1564388438556', 'UF_CRM_1560069180',
                                      'UF_CRM_1560068886', 'TITLE', 'COMMENTS'],
                           'start': next})
        url = 'https://crm.terrakultur.ru/rest/{0}?access_token={1}'.format(method_folder, token)
        r = requests.post(url, headers=headers, data=filt)
        print(r.content)
        client_buffer.append(json.loads(r.content.decode('utf-8'))['result'])
        if 'next' in json.loads(r.content):
            next = json.loads(r.content)['next']
        else:
            break
    for row in client_buffer:
        for client in row:
            client_info.append(client)
    for i in client_info:
        client = models.Client()
        client.id = int(i['ID'])
        client.name = i['TITLE'].replace('&', '-')
        client.address = i['UF_CRM_1560069180']

        if i['UF_CRM_1560069180']:
            if 'москва' in i['UF_CRM_1560069180'].lower():
                client.city = 'Москва'
            elif 'санкт-петербург' in i['UF_CRM_1560069180'].lower():
                client.city = 'Cанкт-петербург'

        client.quantity = i['UF_CRM_1593170402072']
        client.comment = i['COMMENTS']
        client.containers = i['UF_CRM_1560068886']
        client.status = -1
        client.link = 'https://crm.terrakultur.ru/crm/deal/details/' + str(i['ID'] + '/')

        for i in getContact(i['COMPANY_ID']):
            contacts = models.Contacts()

            if i['NAME'] and i['LAST_NAME']:
                contacts.name = i['NAME'] + ' ' + i['LAST_NAME']
            elif i['NAME']:
                contacts.name = i['NAME']
            elif i['LAST_NAME']:
                contacts.name = i['LAST_NAME']

            contacts.address = i['ADDRESS']
            if i['HAS_EMAIL'] == 'Y':
                contacts.email = i['EMAIL'][0]['VALUE']
            if i['HAS_PHONE'] == 'Y':
                contacts.phone = i['PHONE'][0]['VALUE']

            client.contacts.append(contacts)

        db.session.add(client)
    db.session.commit()


def add_team():
    team = models.Team()
    team.workers = '[1, 2]'
    team.name = 'Тестовая команда для тестов'
    team.city = 'Новосибирск'
    db.session.add(team)
    db.session.commit()
    team_re = models.TeamReplacement()
    team_or = models.TeamOrders()
    team_hist = models.TeamHist()
    client_hist = models.TeamClientHistory()
    team_hist.date = '08.06.2020'
    client_hist.client_name = 'Stream plant'
    client_hist.service = '[]'
    team_hist.client_hist.append(client_hist)
    team.team_hist.append(team_hist)
    team_re.team_id = team.id
    team_or.team_id = team.id
    db.session.add(team_re)
    db.session.add(team_or)
    db.session.commit()


def add_report():
    report = models.Report()
    report_list = models.ReportList()
    report.date = '19.05.2020'
    report.comment = 'test'
    report.client = 'Stream plant'
    report.checked = True
    report.comment_last = 'test_last'
    report_list.comment = 'rep_list_comment'
    report_list.sub_tasks = '["Полить", "Попить", "Отдохнуть"]'
    report_list.done = True
    report_list.description = 'Тестовое описание для понимания происходящего'
    report.report_list.append(report_list)
    db.session.add(report)
    db.session.commit()


def add_plants():
    next = 0
    while True:
        filt = json.dumps({'select': ['NAME'], 'start': next})
        url = 'https://crm.terrakultur.ru/rest/{0}?access_token={1}'.format('crm.product.list', token)
        r = requests.post(url, headers=headers, data=filt)
        for i in json.loads(r.content)['result']:
            if '1С' not in i['NAME'] and 'Проба' not in i['NAME'] and 'тест' not in i['NAME']:
                plant = models.Plant()
                plant.name = i['NAME']

                if 'фито' in i['NAME']:
                    plant.type = 'phytowall'
                elif '(К)' in i['NAME']:
                    plant.type = 'circle'
                else:
                    plant.type = 'flower'


                db.session.add(plant)
        if 'next' in json.loads(r.content):
            next = json.loads(r.content)['next']
        else:
            break

    db.session.commit()


def add_floors():
    floor = models.Floor()
    place = models.Place()
    service0 = models.Service()
    service = models.ServicePlant()
    service2 = models.ServicePlant()
    floor.client_id = 1
    floor.num = '2'
    place.name = 'Кабинет директора'
    service.plant_id = 1
    service.plant_name = 'Розочка'
    service.plant_type = 'flower'
    service.plant_dh = '2'
    service.plant_count = 3
    service.plant_guarantee = True
    service2.plant_id = 2
    service2.plant_name = 'Гвоздичка'
    service2.plant_dh = '1'
    service2.plant_type = 'circle'
    service2.plant_count = 2
    service2.plant_guarantee = True
    service0.plants.append(service)
    service0.plants.append(service2)
    place.service.append(service0)
    floor.place_list.append(place)

    db.session.add(floor)
    db.session.commit()


# add_report()
# add_users()
# add_clients()
# add_team()
add_plants()
# add_floors()

# adrs = ['г.Москва, Большой Толмачевский пер., 5', 'г.Москва, Руновский пер., 12', 'г.Москва, ул. Пятницкая, 10 строение 2',
 #       'г.Москва, 2-й Кадашевский пер., 6', 'г.Москва, Кадашевская наб., 10, строен. 1', 'г.Москва, Хилков пер., 2, строение 5',
 #       'г.Москва, 4-й Верхний Михайловский пр-д, 10 корпус 2', 'г.Москва, 2-й Михайловский Верхний пр-д, 12',
  #      'г.Москва, Малая Пироговская ул., 1', 'г.Москва, Малая Пироговская ул., 20 строение 23', 'г.Москва, Хамовнический Вал ул., 28 строение 2',
   #     'г.Москва, Барвиха-2 Кп, Московская обл.', 'г.Москва, ул. Дмитрия Ульянова, 24 корпус 4', 'г.Москва, Ломоносовский просп., 7 корпус 3',
    #    'г.Москва, Ломоносовский просп., 19', 'г.Москва, Ломоносовский просп., 25 к.3']
# clients = models.Client.query.all()
#for i in range(16):
  #  clients[i].address = adrs[i]
# db.session.commit()
