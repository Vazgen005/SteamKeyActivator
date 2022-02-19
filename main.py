from pwinput import pwinput
import steam.webauth as wa
import json
import os
import re


if not os.path.exists('steam_cfg.txt'):
    username = input('Enter your username: ')
    password = pwinput('Enter your password: ')
    with open('steam_cfg.txt', 'w') as f:
        f.write(username + '\n')
        f.write(password)
else:
    with open('steam_cfg.txt', 'r') as f:
        username = f.readline().strip()
        password = f.readline().strip()

user = wa.WebAuth(username, password)
try:
    user.login()
except wa.EmailCodeRequired:
    user.login(email_code=input('Email code: '))
except wa.TwoFactorCodeRequired:
    user.login(twofactor_code=input('2FA code: '))

session = user.session.cookies.get_dict()


def ActivateKey(s_keys: str):
    keys = re.findall('[a-zA-Z0-9]{5}-[a-zA-Z0-9]{5}-[a-zA-Z0-9]{5}', s_keys)
    if not keys:
        print("Not a valid key")
        return
    for a_key in keys:
        r = user.session.post('https://store.steampowered.com/account/ajaxregisterkey/',
                              data={
                                  'product_key': a_key,
                                  'sessionid': session["sessionid"]},
                              headers={
                                  'Cookie': f'sessionid={session["sessionid"]}; birthtime={session["birthtime"]}; lastagecheckage=1-0-1979; Steam_Language=russian; steamCountry={session["steamCountry"]}; steamLoginSecure={session["steamLoginSecure"]}'
                              })
        res = json.loads(r.text)
        if res["success"] == 1:
            for item in res["purchase_receipt_info"]["line_items"]:
                print("[Redeemed]", item["line_item_description"])
        else:
            # Error codes from https://steamstore-a.akamaihd.net/public/javascript/registerkey.js?v=qQS85n3B1_Bi&l
            print('[ERROR CODE]', res['purchase_result_details'])


while True:
    ActivateKey(input('Enter Steam key(s): '))
