import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def setup_driver():
    # install chromedrivermanager so we don't have to path to local chrome
    # and make instance of driver
    s = Service(ChromeDriverManager().install())
    options = Options()
    # options.headless = True
    return webdriver.Chrome(service=s, options=options)


# TODO make url list of items from proshop
def add_item_to_cart(driver, url, max_retry_count=5, duration_between_retry=1):
    # get desired page
    driver.get(url)

    # decline cookies -- MIGHT NOT BE NEEDED (test without)
    cookieDecline = driver.find_element(By.ID, 'declineButton')
    cookieDecline.click()

    # look for add to cart button
    retry_count = 1  # amount of times it will refresh and check again for buy button
    item_added_to_cart = False
    while True:
        try:
            # time.sleep(5)
            add_to_cart_button = driver.find_element(By.CLASS_NAME, 'site-btn-addToBasket-lg')
            add_to_cart_button.click()
            print('add to cart button found and clicked')
            item_added_to_cart = True
            break
        except NoSuchElementException:
            print(f'no buy found -- REFRESHING -- Tries: {retry_count}')
            time.sleep(duration_between_retry)
            driver.refresh()
            print("")
            retry_count += 1
            if retry_count >= max_retry_count:
                break
    return item_added_to_cart


def checkout(driver):
    # TODO fields optimize
    input_fields = {"Name": "karl boge",
                    "Address1": "Ingerslevs Boulevard 29",
                    "ZipCode": "8000",
                    "City": "Aarhus C",
                    "CountryCode": "",
                    "Phone": "88888888",
                    "AnonymousUser_Email": "test@gmail.com",
                    "AnonymousUser_ConfirmEmail": "test@gmail.com"}
    try:
        for i in input_fields:
            # CountryCode should have Denmark as default -- skip it
            if i == "CountryCode":
                continue
            print(i, input_fields[i])
            field_element = driver.find_element(By.ID, i)
            field_element.send_keys(input_fields[i])

        # click next
        driver.find_element(By.CLASS_NAME, 'input__login').click()
        # accept terms and conditions
        driver.find_element(By.ID, 'traidConditionsAnswer').click()

        # make sure PostNord first options are selected (selected by default)
        # TODO

        # click next
        driver.find_element(By.CLASS_NAME, 'btn-success').click()

        # select payment and click
        driver.find_element(By.XPATH, '//*[@id="form-checkout"]/div/div[2]/div[2]/div/ul/li[4]/button').click()
    except NoSuchElementException as exc:
        print(exc)


def check_cart_items(driver):
    # if item is added to cart --> redirects to ./Basket page
    # look for cart element
    try:
        cart_items = driver.find_element(By.ID, 'basketLines')
    except NoSuchElementException as exc:
        print(exc)

    # if no items are found in the cart
    if len(cart_items.find_elements(By.TAG_NAME, 'li')) >= 1:
        print('Items in basket: \n')
        for i in cart_items.find_elements(By.TAG_NAME, 'li'):
            try:
                print("->", i.find_element(By.TAG_NAME, 'b').text)
            except NoSuchElementException:
                print("Error in printing items in cart")
            finally:
                driver.get('https://www.proshop.dk/Basket/CheckOut')
                print('------------------------\n'
                      'Proceeding with checkout')
    else:
        print('Error while adding to cart -- Cart is empty')
        print('Retrying')
        driver.back()


def main():
    # add optional wait - maybe implement a method to wait

    url = "https://www.proshop.dk/Grafikkort/ASUS-GeForce-RTX-3070-DUAL-V2-8GB-GDDR6-RAM-Grafikkort/2958583"
    url2 = "https://www.proshop.dk/Kabinet-Koeler/Corsair-iCUE-QL120-RGB-Black-3-pack-Kabinet-Koeler-120-mm-26-dBA" \
           "/2809664 "

    # setup driver
    driver = setup_driver()

    # time unit to measure how long it is going to take
    start_time = time.time()
    item_added_to_cart = add_item_to_cart(driver, url=url)
    print(f"--- {time.time() - start_time} seconds ---")

    # check if item was successfully added to cart or
    print(item_added_to_cart)
    if item_added_to_cart is not True:
        print("--------------------\n"
              "Item not added to cart or retry count exceeded\n"
              "Exiting")
        driver.close()
        exit()
        # TODO user input later on
        # user_in = input("Retry? - y/n")
        # if user_in == 'y':
        #     driver.close()
        #     main()
        # else:
        #     exit()

    # check if cart items are added correctly and print them out
    check_cart_items(driver)

    # navigate go to checkout
    checkout(driver)

    time.sleep(60)
    driver.close()


if __name__ == '__main__':
    main()
