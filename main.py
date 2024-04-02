import os
import json
import socket
import threading
import time
from tkinter import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import webbrowser
import datetime

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--start-minimized")  # Minimize the window

root = Tk()
nim = StringVar()
password = StringVar()

check_acc = False


def read_json(filename):
    if not os.path.exists(filename):
        return None
    with open(filename) as f:
        data = json.load(f)
    return data


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def is_internet_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def run_bot():
    btn1.configure(text="Jalankan Bot", command=none, default="disabled", cursor="arrow", bg="#2D3133", fg="#202124",
                   activebackground="#2D3133", activeforeground='#202124')
    sts1.configure(text="Menjalankan bot...", fg="#459e48")

    def bot_thread():
        if is_internet_connected():
            data = read_json('data.json')
            if not data:
                btn1.configure(text="Jalankan Bot", bg="#459e48", fg="white", command=run_bot,
                               activebackground="#3C4042", cursor="hand2")
                sts1.configure(text="Atur NIM dan Password terlebih dahulu!", fg="#cd323b")
            else:
                driver = webdriver.Chrome(options=chrome_options)

                btn1.configure(text="Hentikan Bot", bg="#cd323b", fg="white", command=lambda: stop_bot(driver),
                               activebackground="#3C4042", cursor="hand2")
                sts1.configure(text="Bot sedang berjalan...", fg="#459e48")

                driver.get("https://akademik.polban.ac.id/")
                try:
                    WebDriverWait(driver, 10)
                except TimeoutException:
                    stop_bot(driver)

                if is_internet_connected():
                    driver.find_element(By.NAME, "username").send_keys(data['NIM'])
                    driver.find_element(By.NAME, "password").send_keys(data['Password'])
                else:
                    stop_bot(driver)

                if is_internet_connected():
                    driver.find_element(By.NAME, "submit").click()
                else:
                    stop_bot(driver)

                try:
                    WebDriverWait(driver, 10).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                except TimeoutException:
                    print("No alert found within the specified timeout period.")
                    stop_bot(driver)
                except Exception as e:
                    print("An error occurred:", str(e))
                    stop_bot(driver)

                driver.get("https://akademik.polban.ac.id/ajar/absen#")
                try:
                    WebDriverWait(driver, 10)
                except TimeoutException:
                    stop_bot(driver)

                while True:
                    if not is_internet_connected():
                        stop_bot(driver)
                        break

                    buttons = driver.find_elements(By.ID, "simpan_awal")
                    table_rows = driver.find_elements(By.CSS_SELECTOR, "table#jadwal tbody tr")
                    data_perkuliahan = []

                    for row in table_rows:
                        td_elements = row.find_elements(By.TAG_NAME, "td")
                        nama_matkul = td_elements[3].text.strip()
                        jam_perkuliahan = td_elements[7].text.strip()

                        tombol = td_elements[8].find_elements(By.TAG_NAME, "a")
                        tombol_warna = ""
                        for button in tombol:
                            if "btn-danger" in button.get_attribute("class"):
                                if button.text.strip() == "Alpha":
                                    tombol_warna = "Alpha"
                                else:
                                    tombol_warna = "Bukan Waktu Absensi"
                            elif "btn-info" in button.get_attribute("class"):
                                tombol_warna = "Waktunya Absen"
                            elif "btn-warning" in button.get_attribute("class"):
                                tombol_warna = "Dosen Belum Absensi"
                            elif "btn-success" in button.get_attribute("class"):
                                tombol_warna = "Sudah Absensi"

                        data_perkuliahan.append((nama_matkul, jam_perkuliahan, tombol_warna))

                    update_info(data_perkuliahan)

                    if all(data[2] == "Sudah Absensi" for data in data_perkuliahan):
                        stop_bot(driver)
                        break

                    try:
                        buttons = driver.find_elements(By.ID, "simpan_awal")
                        if len(buttons) == 0:
                            print("Sudah absen")
                        else:
                            for button in buttons:
                                button.click()
                                time.sleep(1)
                    except Exception as e:
                        print("An error occurred while clicking the button:", str(e))

                    # now = datetime.datetime.now().strftime("%H:%M:%S")
                    # if any(jam_perkuliahan.replace(" s.d. ", "-") in now and data[2] != "Sudah Absensi" for data
                    #        in data_perkuliahan):
                    #     try:
                    #         while True:
                    #             now = datetime.datetime.now().strftime("%H:%M:%S")
                    #             if any(jam_perkuliahan.replace(" s.d. ", "-") in now and data[
                    #                 2] != "Sudah Absensi" for data in data_perkuliahan):
                    #                 time.sleep(300)
                    #                 print("------- Waktunya Absen")
                    #                 driver.refresh()
                    #             else:
                    #                 break
                    #     except Exception as e:
                    #         print("An error occurred while refreshing the page:", str(e))
                    # else:
                    #     print("-------- Bukan Waktu Absen")
                    #     while True:
                    #         now = datetime.datetime.now().strftime("%H:%M:%S")
                    #         if any(jam_perkuliahan.replace(" s.d. ", "-") in now and data[2] != "Sudah Absensi"
                    #                for data in data_perkuliahan):
                    #             break
                    #         else:
                    #             time.sleep(1)

                    time.sleep(300)

                    try:
                        driver.refresh()
                    except Exception as e:
                        print("An error occurred while refreshing the page:", str(e))

                driver.quit()
        else:
            btn1.configure(text="Jalankan Bot", bg="#459e48", fg="white", command=run_bot,
                           activebackground="#3C4042", cursor="hand2")
            sts1.configure(text="Gagal menghubungkan ke internet", fg="#cd323b")

    threading.Thread(target=bot_thread).start()


def stop_bot(driver):
    btn1.configure(text="Hentikan Bot", command=none, default="disabled", cursor="arrow", bg="#2D3133", fg="#202124",
                   activebackground="#2D3133", activeforeground='#202124')
    sts1.configure(text="Menghentikan bot...", fg="#cd323b")

    def bot_thread():
        driver.quit()
        btn1.configure(text="Jalankan Bot", bg="#459e48", fg="white", command=run_bot,
                       activebackground="#3C4042", cursor="hand2")
        sts1.configure(text="Bot dihentikan", fg="#cd323b")

    threading.Thread(target=bot_thread).start()


def setting():
    settingFrame.place(x=10, y=0)


def close_setting():
    global check_acc
    if not check_acc:
        nim.set("")
        password.set("")
        stsCheck.configure(text="")
        settingFrame.place_forget()


def none():
    pass


def check_account(enim, epassword):
    btnCheck.configure(text="Periksa", command=none, default="disabled", cursor="arrow", bg="#2D3133", fg="#202124",
                       activebackground="#2D3133", activeforeground='#202124')
    stsCheck.configure(text="Memeriksa akun...", fg="#459e48")

    def bot_thread():
        if is_internet_connected():
            global check_acc
            check_acc = True
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://akademik.polban.ac.id/")
            driver.find_element(By.NAME, "username").send_keys(enim)
            driver.find_element(By.NAME, "password").send_keys(epassword)
            driver.find_element(By.NAME, "submit").click()
            try:
                WebDriverWait(driver, 10).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()
            except TimeoutException:
                print("No alert found within the specified timeout period.")
            except Exception as e:
                print("An error occurred:", str(e))

            if driver.current_url == 'https://akademik.polban.ac.id/Mhs':
                stsCheck.configure(text="Akun ditemukan", fg="#459e48")
                btnCheck.configure(text="Simpan", default="normal", cursor="hand2",
                                   command=lambda: save_account(nim.get(), password.get()), background="#459e48",
                                   fg="white", activebackground="#2D3133", activeforeground='#202124')
            else:
                stsCheck.configure(text="Akun tidak ditemukan", fg="#cd323b")
                btnCheck.configure(text="Periksa", default="normal", cursor="hand2",
                                   command=lambda: check_account(nim.get(), password.get()), background="#459e48",
                                   fg="white", activebackground="#2D3133", activeforeground='#202124')

            driver.quit()
            check_acc = False
        else:
            stsCheck.configure(text="Gagal menghubungkan ke internet", fg="#cd323b")

    threading.Thread(target=bot_thread).start()


def open_credits():
    webbrowser.open("https://github.com/FredyKurniadi/autoAbsen")


def save_account(nim, password):
    data = {
        "NIM": nim,
        "Password": password
    }
    write_json('data.json', data)
    close_setting()


def on_entry_change(*args):
    btnCheck.configure(text="Periksa", command=lambda: check_account(nim.get(), password.get()))


def update_info(data_perkuliahan):
    for i in range(6):
        b = Label(infoFrame, text=f"", bg="#202124", fg="white", width="500")
        b.grid(sticky=W, column=0, row=i + 1)
    for index, data in enumerate(data_perkuliahan):
        jadwal = Label(infoFrame, text=f"{data[0]}, {data[1]} | {data[2]}", bg="#202124", fg="white")
        jadwal.grid(sticky=W, column=0, row=index + 1)


if __name__ == "__main__":
    root.title("Auto Absen Akademik POLBAN")
    root.geometry('700x330')
    root.resizable(False, False)
    root.configure(background='#202124')
    root.iconbitmap("app.ico")

    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Credits", command=open_credits)
    menubar.add_cascade(label="Help", menu=filemenu)

    btn1 = Button(root, command=run_bot, text="Jalankan Bot", width=30, height=2, bg="#459e48", fg='white', bd=0,
                  cursor="hand2", activebackground="#2D3133", activeforeground='#202124')
    btn2 = Button(root, command=setting, text="Atur Akun", width=30, height=2, bg="#3C4042", fg='white', bd=0,
                  cursor="hand2", activebackground="#2D3133", activeforeground='#202124')

    statusFrame = Frame(root, width=330, height=40, bg="#202124")
    lbl = Label(statusFrame, text="Status: ", bg="#202124", fg="white")
    sts1 = Label(statusFrame, text="", bg="#202124", fg="white")

    infoFrame = Frame(root, width=330, height=40, bg="#202124")
    lbl2 = Label(infoFrame, text="Info: ", bg="#202124", fg="white")

    btn1.place(relx=0.5, y=40, anchor=CENTER)
    btn2.place(relx=0.5, y=90, anchor=CENTER)

    statusFrame.place(x=10, y=120)
    lbl.grid(sticky=W, column=0, row=0)
    sts1.grid(sticky=W, column=0, row=1)

    infoFrame.place(x=10, y=170)
    lbl2.grid(sticky=W, column=0, row=0)

    settingFrame = Frame(root, width=500, height=330, bg="#202124")
    nimLabel = Label(settingFrame, text="NIM: ", bg="#202124", fg="white")
    nimEntry = Entry(settingFrame, textvariable=nim, width=53, border=0, highlightthickness=6)
    passLabel = Label(settingFrame, text="Password: ", bg="#202124", fg="white")
    passEntry = Entry(settingFrame, textvariable=password, show="*", width=53, border=0, highlightthickness=6)
    btnCheck = Button(settingFrame, text="Periksa", command=lambda: check_account(nim.get(), password.get()), width=15,
                      height=2, border=0, background="#459e48", fg="white", cursor="hand2", activebackground="#2D3133",
                      activeforeground='#202124')
    btnBack = Button(settingFrame, text="Kembali", command=close_setting, width=15, height=2, border=0,
                     background="#3C4042", fg="white", cursor="hand2", activebackground="#2D3133",
                     activeforeground='#202124')
    stsCheck = Label(settingFrame, text="", bg="#202124", fg="#cd323b")

    nimLabel.place(x=130, y=88)
    nimEntry.place(x=200, y=82)
    nimEntry.config(highlightbackground="white", highlightcolor="white")
    passLabel.place(x=130, y=128)
    passEntry.place(x=200, y=122)
    passEntry.config(highlightbackground="white", highlightcolor="white")

    stsCheck.place(x=130, y=160)

    btnBack.place(x=130, y=200)
    btnCheck.place(x=390, y=200)

    nim.trace_add("write", on_entry_change)
    password.trace_add("write", on_entry_change)

    root.config(menu=menubar)
    root.mainloop()
