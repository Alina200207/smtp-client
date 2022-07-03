import pathlib
import re
import socket
import ssl
import base64
import sys
from getpass import getpass

pattern_type_image = re.compile(r'\w*?\.(gif|png|jpg)')
pattern_type_audio = re.compile(r'\w*?\.(mp3|flac|wav)')
pattern_type_video = re.compile(r'\w*?\.(avi|mp4|mpg|mov)')
pattern_type_application = re.compile(r'\w*?\..*')
pattern_error = re.compile(r'.*?Error: ', re.VERBOSE)

def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = socket.recv(65535).decode()
    return recv_data


host_addr = 'smtp.yandex.ru'
port = 465
user_name = input("Введите логин: ")
password = getpass("Введите пароль: ")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((host_addr, port))
        except:
            print("Проверьте подключение к интернету")
            sys.exit()
        client = ssl.wrap_socket(client)
        print(client.recv(1024))
        print(request(client, 'ehlo {user_name}'))
        base64login = base64.b64encode(user_name.encode()).decode()
        base64password = base64.b64encode(password.encode()).decode()
        print(request(client, 'AUTH LOGIN'))
        print(request(client, base64login))
        res = re.search(pattern_error, request(client, base64password))
        if res:
            print("Введен неправильный логин пользователя или пароль")
            sys.exit()
        print(request(client, f'MAIL FROM:{user_name}'))
        print(request(client, f"RCPT TO:{user_name}"))
        print(request(client, 'DATA'))
        msg = ''
        with open('headers.txt', 'r') as file:
            msg += file.read()
        msg += '\n'
        tab = '\t'
        bound = "--=-boundar-9879"
        msg += 'Content-Type: multipart/mixed;\n' + tab + f"boundary=\"{bound}\""
        msg += '\n\n\n'
        msg += f'--{bound}\n'
        msg += "Content-Transfer-Encoding: 7bit\nContent-Type: text/plain\n\n"
        with open('msg.txt') as file:
            msg += file.read() + '\n'
        for f in pathlib.Path("attachments").iterdir():
            general_type = ''
            subtype = ''
            find_image = re.search(pattern_type_image, f.name)
            find_audio = re.search(pattern_type_audio, f.name)
            find_video = re.search(pattern_type_video, f.name)
            find_application = re.search(pattern_type_application, f.name)
            if find_image:
                general_type = "image"
                subtype = find_image.group(1)
            elif find_audio:
                general_type = "audio"
                subtype = find_audio.group(1)
            elif find_video:
                general_type = "video"
                subtype = find_video.group(1)
            elif find_application:
                general_type = "application"
                subtype = "octet-stream"
            else:
                continue
            if subtype == "jpg":
                subtype = "jpeg"
            msg += f"--{bound}\n"
            msg += "Content-Disposition: attachment;\n" + tab + f'filename=\"{f.name}\"\n'
            msg += f"Content-Transfer-Encoding: base64\nContent-Type: {general_type}/{subtype};\n" + tab
            msg += f"name=\"{f.name}\""
            msg += "\n\n"
            with f.open('rb') as fil:
                msg += base64.b64encode(fil.read()).decode()
            msg += '\n'
        msg += f'--{bound}--\n.'
        print(msg)
        print(request(client, msg))


if __name__ == "__main__":
    main()
