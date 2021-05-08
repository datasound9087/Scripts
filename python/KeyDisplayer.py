from pynput.keyboard import Listener

def main():

    print("Running")
    with Listener(on_press=on_press) as listener:
        listener.join()

def on_press(key):
    print("{0}".format(key))

if __name__ == "__main__":
    main()