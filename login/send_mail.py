import os
from django.core.mail import send_mail

os.environ['DJANGO_SETTINGS_MODULE'] = 'ChearBuy.settings'

if __name__ == '__main__':

    send_mail(
        'Register Check From Cheaper Buy',
        'This email is to make sure it is you to register by this email',
        'euwcheaperbuy@sina.com',
        ['chyweichen@163.com'],
    )