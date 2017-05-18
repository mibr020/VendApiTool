from Tkinter import *
import os
import subprocess
import csv
import glob
import requests
import grequests
import logging
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import re
import json
import time
import sys
import traceback
import dateutil.parser
import datetime
import pytz


# mazuko token 5Ladw3FITzySnkokRyIvb:ZBydMk0a5kr8qQISLN

# DELETE url "https://<insertdomainprefix>.vendhq.com/api/2.0/customers/%s"

class GUI:
    def __init__(self, master):
        # GLOBAL VARIABLES
        self.customersUrl = "https://%s.vendhq.com/api/customers?code=%s"
        self.registerUrl = "https://%s.vendhq.com/api/registers"
        self.customersDeleteEndpoint = "https://%s.vendhq.com/api/2.0/customers/%s"
        self.productsDeleteEndpoint = "https://%s.vendhq.com/api/products/%s"
        self.usersDeleteEndpoint = "https://%s.vendhq.com/api/1.0/users/%s"
        self.giftcardsDeleteEndpoint = "https://%s.vendhq.com/api/2.0/balances/gift_cards/%s"
        self.salesDeleteEndpoint = "https://%s.vendhq.com/api/register_sales"

        self.csvSize = 0
        self.successfullySentRequests = []
        self.dictOfUnsentRequests = {}

        self.getSalesEndpoint = "https://%s.vendhq.com/api/register_sales/%s"

        self.page = 1
        self.pagecount = ""
        self.salecount = ""

        self.domain_prefix = StringVar()
        self.token = StringVar()

        self.headers = {"content-type": "application/json",
                        "Authorization": "Bearer %s"}

        self.master = master
        self.TOOL_SELECTED = StringVar()
        self.CUSTOMER_CSV = ''
        self.CUSTOMER_IDS = []
        self.DOMAIN_PREFIX = ''
        self.TOKEN = ''
        self.HEADERS = [['Content-Type', 'application/json'], ['Authorization', 'Bearer %s']]
        self.PAYLOAD = {"page": self.page}
        self.LOG_FILENAME = '%s.log'
        self.COMMANDS = {}

        self.currentFrames = []
        self.frameButtons = []

        # Create an instance of a frame
        toolSelectFrame = Frame(master)
        toolSelectFrame.pack(side=TOP, anchor=W, fill=X, expand=YES)

        # Permits the ability to call get on variable
        toolSelected = StringVar(master)
        # Call the callback function when value is changed
        toolSelected.trace('w', self.callback)
        # Set the defaut option for the dropdown menu
        toolSelected.set("Select option")

        self.TOOL_SELECTED = toolSelected

        # Top Frame of the window
        self.topFrame = Frame(master)
        self.topFrame.pack(side=TOP)

        # Bottom Compartment of the top frame
        self.topBottomHalfFrame = Frame(self.topFrame)
        self.topBottomHalfFrame.pack(side=TOP)

        # pack() Specific details box in the bottom compartment of the top frame
        self.toolSpecificLabelFrame = LabelFrame(self.topBottomHalfFrame, text="Specific details", padx=10, pady=10)
        self.toolSpecificLabelFrame.pack(side=LEFT)

        # Center frame of the window
        self.centerFrame = Frame(master)
        self.centerFrame.pack(side=TOP)

        # Bottom Frame of the window
        self.bottomFrame = Frame(master)
        self.bottomFrame.pack(side=BOTTOM)

        # Create a box with a label header. The content of the box will be the dropdown box (optionMenuDropdown)
        self.optionMenuLabelFrame = LabelFrame(toolSelectFrame, text="Select tool", padx=10, pady=10)
        self.optionMenuLabelFrame.pack(padx=15, pady=15)

        # Pack() Required details box in the top compartment of the top frame
        self.topLabelFrame = LabelFrame(self.topFrame, text="Required details", padx=10, pady=10)
        self.topLabelFrame.pack(padx=15, pady=15)

        # pack domain prefix label text in the required details box
        self.dpLabel = Label(self.topLabelFrame, text="domain prefix", justify=RIGHT)
        self.dpLabel.pack(side=LEFT)

        # pack Domain prefix input in the required details box
        self.dpEntry = Entry(self.topLabelFrame, textvariable=self.domain_prefix)
        self.dpEntry.pack(side=LEFT)

        # Pack Token Label text in the required details box
        self.tLabel = Label(self.topLabelFrame, text="token", justify=RIGHT)
        self.tLabel.pack(side=LEFT)

        # Pack Token input in the required details box
        self.tEntry = Entry(self.topLabelFrame, textvariable=self.token)
        self.tEntry.pack(side=LEFT, fill=X)

        # Pack Status labelframe in the bottom Frame
        self.statusLabelFrame = LabelFrame(self.bottomFrame, text="Status", width=450, height=80, padx=10, pady=10)
        self.statusLabelFrame.pack(side=LEFT, padx=15, pady=15)
        self.text = Text(self.statusLabelFrame, width=80, height=10, padx=15, pady=15)
        self.text.pack()

        # Pack the dropdown box in the option menu in the top compartment of the top frame
        optionMenuDropdown = OptionMenu(self.optionMenuLabelFrame, toolSelected, "Select option", "Bulk Delete",
                                        "Void Sales").pack()

    # Need to my a dictionary of all the commands that can be run accoding to th dropdown options
    # Default option should be "select n option" which by default runs default layout
    # once an option is sleected,

    def void_sales_between_two_dates(self):
        self.clear_frame()

        date_to = StringVar()
        date_from = StringVar()
        time_zone = StringVar()
        sale_statuses = StringVar()

        # Date to label text
        self.dtLabel = Label(self.toolSpecificLabelFrame, text="Date to", justify=RIGHT)
        self.dtLabel.pack(side=LEFT)
        self.currentFrames.append(self.dtLabel)

        # Date to input
        self.dtEntry = Entry(self.toolSpecificLabelFrame, textvariable=date_to)
        self.dtEntry.pack(side=LEFT)
        self.currentFrames.append(self.dtEntry)

        # Date from text
        self.dfLabel = Label(self.toolSpecificLabelFrame, text="Date from", justify=RIGHT)
        self.dfLabel.pack(side=LEFT)
        self.currentFrames.append(self.dfLabel)

        # Date from input
        self.dfEntry = Entry(self.toolSpecificLabelFrame, textvariable=date_from)
        self.dfEntry.pack(side=LEFT)
        self.currentFrames.append(self.dfEntry)

        # Time zone text
        self.tzLabel = Label(self.toolSpecificLabelFrame, text="Time zone", justify=RIGHT)
        self.tzLabel.pack(side=LEFT)
        self.currentFrames.append(self.tzLabel)

        # time zone input
        self.tzEntry = Entry(self.toolSpecificLabelFrame, textvariable=time_zone)
        self.tzEntry.pack(side=LEFT)
        self.currentFrames.append(self.tzEntry)

        # sale statuses text
        self.ssLabel = Label(self.toolSpecificLabelFrame, text="Sale statuses (Leave empty to do all sales)",
                             justify=RIGHT)
        self.ssLabel.pack(side=LEFT)
        self.currentFrames.append(self.ssLabel)

        # sale statuses input
        self.ssEntry = Entry(self.toolSpecificLabelFrame, textvariable=sale_statuses)
        self.ssEntry.pack(side=LEFT)
        self.currentFrames.append(self.ssEntry)

        self.action = IntVar()

        radioButtonVoid = Radiobutton(self.toolSpecificLabelFrame, text="Void", variable=self.action, value=1)
        radioButtonVoid.pack(anchor=W)
        self.currentFrames.append(radioButtonVoid)

        radioButtonUpdate = Radiobutton(self.toolSpecificLabelFrame, text="Update", variable=self.action, value=2)
        radioButtonUpdate.pack(anchor=W)
        self.currentFrames.append(radioButtonUpdate)

        # Update sale button
        self.updateSalesButton = Button(self.toolSpecificLabelFrame, text="Update Sales",
                                        command=lambda: self.format_request(date_to, date_from, time_zone,
                                                                            sale_statuses))
        self.updateSalesButton.pack(side=LEFT, fill=X, expand=YES)
        self.currentFrames.append(self.updateSalesButton)
        self.currentFrames.append(self.updateSalesButton)

    def anything_bulk_delete(self):
        # Clear frame/canvas
        self.clear_frame()

        # Permits the ability to call get on frame
        entityToDelete = StringVar(self.master)
        # Set the defaut option for the dropdown menu
        entityToDelete.set("Select option")

        # Create a box with a label header. The content of the box will be the dropdown box (optionMenuDropdown)
        entityLabelFrame = LabelFrame(self.topFrame, text="Select entity to delete", padx=10, pady=10)
        entityLabelFrame.pack(padx=15, pady=15)
        self.currentFrames.append(entityLabelFrame)

        optionMenuDropdown = OptionMenu(entityLabelFrame, entityToDelete, "Select option", "Products", "Customers",
                                        "Users", "GiftCards").pack()

        self.text.insert(END,
                         "Make sure the CSV is named in this convention: {domainPrefix}-{entityToDelete}.csv" + "\n")
        self.text.insert(END, "For example: to bulk delete products for Mazuko, mazuko-products.csv" + "\n")
        self.text.see(END)
        self.text.update()

        #   self.getButton = Button(self.topFrame, text="Get CSV", command=lambda: self.get_csv(domain_prefix, token))
        #   self.getButton.pack(side=LEFT, fill=X, expand=YES)
        #   self.currentFrames.append(self.getButton)

        self.del_cus_button = Button(self.topFrame, text="Delete entities",
                                     command=lambda: self.del_entities(entityToDelete.get()))
        self.del_cus_button.pack(side=LEFT, fill=X, expand=YES)
        self.currentFrames.append(self.del_cus_button)
        self.frameButtons.append(self.del_cus_button)

    def number_of_rows(self, entity):
        with open(self.domain_prefix.get() + '-' + entity + '.csv', 'rb') as csvfile:
            rowCountReader = csv.reader(csvfile, delimiter=",")
            data = list(rowCountReader)
            self.csvSize = len(data)
            return self.csvSize

        print "Done counting the rows: %s" % (rowCount)
        return rowCount

    def call_api(self, index, requests, row_count):
        if (index != 0) and (index % 300 == 0):
            result = grequests.map(requests)
            print result
            self.text.insert(END, "Check terminal for request results" + "\n")
            self.text.see(END)
            self.text.update()

            self.text.insert(END, "300 request mark reached, taking a 5 min break" + "\n")
            self.text.see(END)
            self.text.update()
            self.log_results()

            time.sleep(300)

            return result
        # check if this si the last row, index + 2 because index starts at 0 and another 1 for header row
        elif row_count == index + 2:
            result = grequests.map(requests)
            print result
            self.text.insert(END, "Check terminal for request results" + "\n")
            self.text.see(END)
            self.text.update()

            self.text.insert(END, "end of file reached, fuck you sumeet." + "\n")
            self.text.see(END)
            self.text.update()
            self.log_results()

            time.sleep(300)

            return result
        else:
            return False

    def retry_time_handler(self, response):
        print response
        print "The rate limit is %s" % (response["limits"])

        retry_after = dateutil.parser.parse(response["retry-after"])

        utc = pytz.UTC

        now = utc.localize(datetime.datetime.utcnow())

        print (retry_after - now).seconds

        return (retry_after - now).seconds + 2

    def remove_successful_requests(self, requests, responses):
        for index, row in enumerate(responses):
            self.log_info(str(row.url))
            print row.status_code
            if row.status_code == 200 or row.status_code == 204:
                print row.content
                if "error" in row.json():
                    print "Unable to delete entity via api due to %s" % (row.json()["details"])
                del requests[index]
            if row.status_code == 429:
                return (self.retry_time_handler(row.json()), requests)
            if row.status_code == 404:
                print "encountered 404 for %s, deleting it from the request list" % (row.url)
                del requests[index]
        return (0,requests)

    def del_entities(self, entity):
        # return if fields are empty
        if self.domain_prefix.get() == "" or self.token.get() == "":
            self.text.insert(END, "ERROR - Fill required details" + "\n")
            self.text.see(END)
            self.text.update()
            return

        endpoint = self.generate_endpoint(entity)

        if entity == "GiftCards":
            self.void_gift_cards(entity, endpoint)
            return False

        result = ""

        print self.domain_prefix.get() + '-' + entity + '.csv'

        try:
            with open(self.domain_prefix.get() + '-' + entity + '.csv', 'rb') as vcsv:
                reader = csv.DictReader(vcsv)
                headers = {
                    self.HEADERS[0][0]: self.HEADERS[0][1],
                    self.HEADERS[1][0]: self.HEADERS[1][1] % (self.token.get()),
                }
                requests = []

                print self.number_of_rows(entity)

                for index, row in enumerate(reader):
                    requests.append(grequests.delete(endpoint % (self.domain_prefix.get(), row['id']), headers=headers))

                # batch requests into groups of 300
                # on any batch that has any response of 429, wait N seconds (determined by retry_time_handler)
                # continue until another 429, or no more requests
                # at first, let's just stop when we hit a 429 ( exit(0) )

                self.send_requests(requests)

        except IndexError as e:
            print "index error"
            print e
        except LookupError as e:
            print "lookup error"
            print e
        except:
            print sys.exc_info()
            response = []
            print result

            self.text.insert(END, "ERROR - couldn't open the CSV perhaps, check the terminal" + "\n")
            self.text.see(END)
            self.text.update()

        return False

    def void_gift_cards(self, entity, endpoint):
        with open(self.domain_prefix.get() + '-' + entity + '.csv', 'rb') as vcsv:
            reader = csv.DictReader(vcsv)
            headers = {
                self.HEADERS[0][0]: self.HEADERS[0][1],
                self.HEADERS[1][0]: self.HEADERS[1][1] % (self.token.get()),
            }
            response = []
            for index, row in enumerate(reader):
                self.log_request_responses([row['number']])
                response.append(grequests.delete(endpoint % (self.domain_prefix.get(), row['number']), headers=headers))

                # Calls api and is rate limit concious
                limit_reached = self.call_api(index, response)

                if limit_reached:
                    response = []

        self.log_results()

        self.log_request_responses(grequests.map(response))

        return False

    def generate_endpoint(self, entity):
        if entity == 'Products':
            return self.productsDeleteEndpoint
        elif entity == 'Users':
            return self.usersDeleteEndpoint
        elif entity == 'Customers':
            return self.customersDeleteEndpoint
        elif entity == 'GiftCards':
            return self.giftcardsDeleteEndpoint
        return False

    def setup_headers(self):
        headers = {
            self.HEADERS[0][0]: self.HEADERS[0][1],
            self.HEADERS[1][0]: self.HEADERS[1][1] % (self.token.get()),
        }

        return headers

    def getSale(self, saleId):
        headers = self.setup_headers()
        return requests.get(self.getSalesEndpoint % (self.domain_prefix.get(), saleId), headers=headers).json()

    def log_info(self, info):
        self.text.insert(END, info + "\n")
        self.text.see(END)
        self.text.update()

    def find_index_of_failed_request(self, sent_responses):
        for index, response in enumerate(sent_responses):

            if (response.status_code == 200) and (response.status_code == 204):
                self.log_info("Skipping sale index number - " + str(index) + " url - " + response.url)

            # if response.status_code == 404:
            #     self.log_info("Skipping sale index number - " + str(index) + " url - " + response.url)
            #     continue
            #
            # if (response.status_code != 200) and (response.status_code != 204):
            #     print "Index number %s was the first failed request with a status of %s" % (index, response.status_code)
            #     return index
            #
            # self.log_info("Preparing request for row - " + str(index + 2))
            #
            # print response

            self.successfullySentRequests.append(response.json())
        return False

    def send_requests(self, requests):

        # failedRequestIndex = self.find_index_of_failed_request(sent_responses)

        # if not failedRequestIndex:
        #     print "There wasn't a failed status, method returned %s" % (failedRequestIndex)
        #     return True
        #
        # failedRequests = sent_requests[failedRequestIndex:len(sent_requests) - 1]

        print "Sending batch of requests"

        responses = grequests.map(requests[0:499])

        # print sent_responses
        delay,new_requests = self.remove_successful_requests(requests, responses)

        if delay:
            print "Sleeping for %s seconds" % (str(delay))
            time.sleep(delay)

        if len(new_requests) > 0:
            print "Retrying %s requests after sleeping for a 5 seconds" % (len(new_requests))
            time.sleep(5)
            self.send_requests(new_requests)

        print 'Done sending requests'

    def get_sales(self):
        # Disable the most recent button clicked
        self.frameButtons[-1].config(state="disabled")

        if self.domain_prefix.get() == "" or self.token.get() == "":
            self.text.insert(END, "ERROR - Fill required details" + "\n")
            self.text.see(END)
            self.text.update()
            return

        headers = self.setup_headers()
        requests = []

        # Get the size of the csv (number of rows)
        csv_size = self.number_of_rows('Sales')

        try:
            with open(self.domain_prefix.get() + '-Sales.csv', 'rb') as csvfile:
                reader = csv.DictReader(csvfile)
                self.text.insert(END, "Beggining to GET sales from the CSV" + "\n")
                self.text.see(END)
                self.text.update()

                for index, row in enumerate(reader):
                    # Setup  a list of unsent requests so they can be sent over in bulk asyncronousley (fuck spelling)
                    requests.append(
                        grequests.get(self.getSalesEndpoint % (self.domain_prefix.get(), row['id']), headers=headers))
                    # Check if limit is reached or end of file is reached, if so then it sends the get sales requests in bulk and sleeps for 5 mins

                sent_responses = grequests.map(requests)

                self.send_requests(sent_responses, requests)

                # limit_reached = self.call_api(index, sales, csv_size)

                # If sale requests are sent then begin to void all the sales and clear the unsent requests array
                voidResult = self.void_sales_from_csv(self.successfullySentRequests)

        except IndexError as e:
            print "index error"
            print e
        except LookupError as e:
            print "lookup error"
            print e
        except:
            print sys.exc_info()
            print traceback.print_exc()

            self.text.insert(END, "ERROR - couldn't open the CSV perhaps, check the terminal" + "\n")
            self.text.see(END)
            self.text.update()

        return True

    def void_sales_from_csv(self, sales):
        # To hold unsent requets
        requests = []
        headers = self.setup_headers()

        for index, value in enumerate(sales):
            sale = value["register_sales"]

            if sale == []:
                self.text.insert(END, "### Sale on row " + str(index + 2) + " is empty, skipping that bitch." + "\n")
                self.text.see(END)
                self.text.update()

                print "skipping empty sale"

                continue

            self.log_info("### Voiding sale id " + sale[0]['id'] + "on row " + str(index + 2))

            sale[0]['status'] = "VOIDED"
            requests.append(grequests.post(self.salesDeleteEndpoint % (self.domain_prefix.get()), headers=headers,
                                           data=json.dumps(sale[0])))

        self.log_info("### About to void them motherfuckers" + "\n")

        sent_responses = grequests.map(requests)

        self.text.insert(END, "### About to retry failed requests" + "\n")
        self.text.see(END)
        self.text.update()

        print sent_responses

        self.successfullySentRequests = []

        self.send_requests(sent_responses, requests)

        print "Done voiding sales from CSV"

        return

    def updateSale(self, sale):
        headers = self.setup_headers()
        # print json.loads(json.dumps(sale))[0]
        # print json.dumps(sale)
        return grequests.post(self.salesDeleteEndpoint % (self.domain_prefix.get()), headers=headers,
                              data=json.dumps(sale))

    def setup_void_sales(self):
        self.clear_frame()

        self.void_sales_button = Button(self.topFrame, text="Void Sales", command=lambda: self.get_sales())
        self.void_sales_button.pack(side=LEFT, fill=X, expand=YES)
        self.currentFrames.append(self.void_sales_button)
        self.frameButtons.append(self.void_sales_button)

    def void_sales(self):
        if self.domain_prefix.get() == "" or self.token.get() == "":
            self.text.insert(END, "ERROR - Fill required details" + "\n")
            self.text.see(END)
            self.text.update()
            return

        response = []

        try:
            with open(self.domain_prefix.get() + '-Sales.csv', 'rb') as csv_to_count:
                csv_row_count = self.number_of_rows(csv_to_count)

            sales = self.get_sales(csv_row_count)

            with open(self.domain_prefix.get() + '-Sales.csv', 'rb') as csvfile:

                reader = csv.DictReader(csvfile)
                self.text.insert(END, "Beggining to Void sales in the CSV" + "\n")
                self.text.see(END)
                self.text.update()

                sales = []

                for index, row in enumerate(reader):

                    sale = self.getSale(row['id'])['register_sales']

                    if sale == []:
                        print "Sale # " + row['id'] + " is empty, skipping to next sale"
                        continue

                    self.text.insert(END, "### Voiding sale id " + row['id'] + "on row " + str(index + 2) + "\n")
                    self.text.see(END)
                    self.text.update()

                    sale[0]['status'] = "VOIDED"
                    response.append(self.updateSale(sale[0]))

                    # Calls api and is rate limit concious
                    limit_reached = self.call_api(index * 2, response, csv_row_count)

                    if limit_reached:
                        response = []

        except IndexError as e:
            print "index error"
            print e
        except LookupError as e:
            print "lookup error"
            print e
        except:
            print sys.exc_info()

            self.text.insert(END, "ERROR - couldn't open the CSV perhaps, check the terminal" + "\n")
            self.text.see(END)
            self.text.update()

        return False

    def log_request_responses(self, responses):
        for response in responses:
            self.text.insert(END, str(response) + "\n")
            self.text.see(END)
            self.text.update()

    def re_version_customer_sales(self):
        self.clear_frame()

    def merge_customers(self):
        self.clear_frame()

        Label(self.statusLabelFrame, text="Merging customer tool is not ready").pack()

        return False

        self.topBottomHalfFrame = Frame(self.topFrame)
        self.topBottomHalfFrame.pack(side=TOP)

        self.toolSpecificLabelFrame = LabelFrame(self.topBottomHalfFrame, text="Specific details", padx=10, pady=10)
        self.toolSpecificLabelFrame.pack(side=LEFT)

        master_customer_code = StringVar()
        customer_codes_to_merge = StringVar()

        # master customer to label text
        self.mccLabel = Label(self.toolSpecificLabelFrame, text="Master customer code", justify=RIGHT)
        self.mccLabel.pack(side=LEFT)
        self.currentFrames.append(self.mccLabel)

        # master customer to input
        self.mccEntry = Entry(self.toolSpecificLabelFrame, textvariable=master_customer_code)
        self.mccEntry.pack(side=LEFT)
        self.currentFrames.append(self.mccEntry)

        # master customer to label text
        self.cLabel = Label(self.toolSpecificLabelFrame, text="Customers to merge (seperated by commas)", justify=RIGHT)
        self.cLabel.pack(side=LEFT)
        self.currentFrames.append(self.cLabel)

        # master customer to input
        self.cEntry = Entry(self.toolSpecificLabelFrame, textvariable=customer_codes_to_merge)
        self.cEntry.pack(side=LEFT)
        self.currentFrames.append(self.cEntry)

        self.mergeButton = Button(self.centerFrame, text="Merge customers",
                                  command=lambda: self.begin_merging(master_customer_code, customer_codes_to_merge))
        self.mergeButton.pack(side=LEFT, fill=X, expand=YES)
        self.currentFrames.append(self.mergeButton)
        self.frameButtons.append(self.mergeButton)

    def begin_merging(self, master_customer_code, customer_codes_to_merge):

        customerCodes = re.split(', |,', customer_codes_to_merge.get())

        saleResponse = self.register_sales("")

        customer_id = self.validate_customer(master_customer_code.get())

        self.update_sales = []

        for customerCode in customerCodes:
            if customer_id == False:
                return False
            print "master id is %s" % (customer_id)
            for sale in saleResponse["register_sales"]:
                try:
                    if sale["customer"]["customer_code"] == customerCode:
                        print sale["invoice_number"]
                        Label(self.statusLabelFrame,
                              text="Merging customer from invoice number #%s" % (sale["invoice_number"]),
                              fg="red").pack()
                        sale["customer_id"] = customer_id
                        self.update_sales.append(self.update_sale(sale))
                        # self.update_sales.append(self.put_sale(sale["id"], customer_id))
                except:
                    continue

            results = grequests.map(self.update_sales)
            self.update_sales = []
            Label(self.statusLabelFrame, text=results, fg="red").pack()

        return False

    def update_sale(self, sale):
        return grequests.post(self.updateSalesUrl % (self.domain_prefix.get()), headers=self.headers,
                              params=self.PAYLOAD, data=json.dumps(sale))

    def validate_customer(self, customerCode):
        self.headers = {"content-type": "application/json",
                        "Authorization": "Bearer %s" % (self.token.get())}

        try:
            response = requests.get(self.customersUrl % (self.domain_prefix.get(), customerCode), headers=self.headers,
                                    params=self.PAYLOAD).json()["customers"][0]["id"]
            return response
        except:
            print "Customer code does not exist"
            return False

    def select_option(self):
        self.clear_frame()

    def callback(self, *args):
        print "Callback is running"

        # Dictionary of all the possible options/tools
        self.COMMANDS = {
            "Select option": self.select_option,
            "Bulk Delete": self.anything_bulk_delete,
            "Void Sales": self.setup_void_sales,
            "Void sales between two dates": self.void_sales_between_two_dates,
            "Re-version customer sales": self.re_version_customer_sales,
            "Merge customers": self.merge_customers
        }

        # Select the tool chosen and evoke it
        func = self.COMMANDS[self.TOOL_SELECTED.get()]
        func()

    # Clear all the frames from the previous tool selected
    def clear_frame(self):
        for widget in self.currentFrames:
            widget.pack_forget()
            self.currentFrames = []

    def format_request(self, date_to, date_from, time_zone, sale_statuses):
        print date_to.get(), date_from.get(), time_zone.get(), sale_statuses.get()

        # Update all sales
        if sale_statuses.get() == "":
            status = ""
            print "yeap"

        fmt = "%Y-%m-%d %H:%M:%S"

        utc = pytz.utc
        utc.zone

        try:
            timezone = timezone(time_zone.get())
            print "timezone shii worked %s" % (timezone)
        except:
            print time_zone.get()
            print "time zone given is the wrong format"
            return False

        if date_from == "":
            date_from = date_to

        # Changes date and time entered to a datetime object
        dateToFormat = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
        dateFromFormat = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")

        # Localize the datetime to the timezone specified
        dateToDateTime = timezone.localize(
            datetime(dateToFormat.year, dateToFormat.month, dateToFormat.day, dateToFormat.hour, dateToFormat.minute,
                     dateToFormat.second))
        dateFromDateTime = timezone.localize(
            datetime(dateFromFormat.year, dateFromFormat.month, dateFromFormat.day, dateFromFormat.hour,
                     dateFromFormat.minute, dateFromFormat.second))

        # Convert the datetime to UTC time
        self.dateToUTC = dateToDateTime.astimezone(utc)
        self.dateFromUTC = dateFromDateTime.astimezone(utc)

        # String format of the UTC time to help match with datetime format in API responses
        self.strdateToUTC = dateToUTC.strftime(fmt)
        self.strdateFromUTC = dateFromUTC.strftime(fmt)

        print strdateToUTC, strdateFromUTC

        saleResponse = register_sales(status)

        # Check how many pages the request has
        if sale_statuses.get() == "":
            check_pages(saleResponse)

        return False

    def register_sales(self, status):
        self.headers = {"content-type": "application/json",
                        "Authorization": "Bearer %s" % (self.token.get())}

        print self.headers
        return requests.get(self.salesUrl % (self.domain_prefix.get(), status), headers=self.headers,
                            params=self.PAYLOAD).json()

    def check_pages(self, saleResponse):
        if 'pagination' in salesResponse:
            self.pagecount = salesResponse["pagination"]["pages"]
            self.salecount = salesResponse["pagination"]["results"]
            print "There is a total of %s sales" % (salesCount)
        else:
            self.pagecount = 1
            print "There's only 1 page worth of sales"
        return False

    def update_sales():
        while (not self.page > pagecount):
            print "hello"
            for status in statusList:
                self.check_pages(status)
                print "Looking for %s sales" % (status)
                # self.check_pages(status)
                self.page = 1
                salesResponse = register_sales(status)

                # If API limit is reached then sleep for 350 seconds
                if "retry-after" in salesResponse:
                    print "Rate limit reached - Taking a 5.5 min breather"
                    time.sleep(350)
                    salesResponse = register_sales(status)

                print "----- Editing tickets from page %s -----" % (self.page)
                for sale in salesResponse["register_sales"]:

                    # Change sale time to a datetime object
                    saleDate = datetime.strptime(sale["created_at"], "%Y-%m-%d %H:%M:%S")

                    # Localize the datetime to UTC timezone
                    saleDateUTC = utc.localize(
                        datetime(saleDate.year, saleDate.month, saleDate.day, saleDate.hour, saleDate.minute,
                                 saleDate.second))

                    # format the datetime to UTC time. This is needed to compare the two datetimes (Formating issues)
                    formatedSaleDate = saleDateUTC.astimezone(utc)

                    print "_______________________________________________________________\n"
                    print "| Sale created at: %s                           |" % (saleDate)

                    # Check if sale is between the two dates then action it
                    if self.dateFromUTC != self.dateToUTC:
                        if self.dateFromUTC < formatedSaleDate < self.dateToUTC:
                            print "| Before date specified: %s                       |" % (self.strdateToUTC)
                            print "| After date specified: %s                         |" % (self.strdateFromUTC)
                            print "| *** Sale Invoice %s is between the set datetimes ***    |" % (
                            sale["invoice_number"])
                            sale["id"] = "VOIDED"
                            voidedUrls.append(voidSale(sale))
                            print "| *** Sale is added to the list of sales to be voided *** |"
                            voidedCount += 1
                            writer.writerow([sale["invoice_number"]])
                            # Only looks for sales before the dateTo datetime
                    else:
                        if formatedSaleDate < self.dateToUTC:
                            print "| Before date specified: %s                              |" % (
                            self.self.strdateToUTC)
                            print "| *** Sale Invoice %s is before the set datetime specified *** |" % (
                            sale["invoice_number"])
                            sale["status"] = "VOIDED"
                            voidedUrls.append(voidSale(sale))
                            print "| *** Sale is added to the list of sales to be voided ***      |"
                            voidedCount += 1
                            writer.writerow([sale["invoice_number"]])

                    print "_______________________________________________________________"

                    results = grequests.map(voidedUrls)
                    print results
                    writer.writerow([results])
                    print "#### Voided %s sales --> moving to the next page if applicable ####" % (voidedCount)
                    self.page += 1
                    voidedUrls = []
                    time.sleep(0.5)
        return False

    def get_csv(self, domain_prefix, token):

        # return if fields are empty
        if domain_prefix.get() == "" or token.get() == "":
            Label(self.statusLabelFrame, text="ERROR - Fill required details", fg="red").pack()
            return

        Label(self.statusLabelFrame, text="fetching CSV...", fg="red").pack(side=TOP)
        # Listens for outputs from terminal
        pipe = subprocess.Popen("./vend-customer-export -d " + domain_prefix.get() + " -t " + token.get(), shell=True,
                                stdout=subprocess.PIPE).stdout
        # reads every output and puts them into array
        output = pipe.read()

        Label(self.statusLabelFrame, text=output, fg="red").pack(side=TOP)
        # Saves the file location for the most recent added csv file in folder path
        self.CUSTOMER_CSV = max(glob.iglob('*.[Cc][Ss][Vv]'), key=os.path.getctime)
        Label(self.statusLabelFrame, text=self.CUSTOMER_CSV).pack()

        # Update domain prefix and token
        self.DOMAIN_PREFIX = domain_prefix.get()
        self.TOKEN = token.get()

        # Inserts token into bearer header
        self.HEADERS[1][1] = self.HEADERS[1][1] % (self.TOKEN)

        print self.CUSTOMER_CSV

        return False

    def del_cus(self):
        os.chdir('/Users/Mazin/Documents/Del_all_customers')
        with open(self.CUSTOMER_CSV, 'rb') as vcsv:
            reader = csv.DictReader(vcsv)
            next(reader)  # Skips the first row (WALKIN customer id)
            headers = {
                self.HEADERS[0][0]: self.HEADERS[0][1],
                self.HEADERS[1][0]: self.HEADERS[1][1],
            }
            response = []
            for row in reader:
                if row['deleted_at'] == "":
                    response.append(
                        grequests.delete(self.DELETE_ENDPOINT % (self.DOMAIN_PREFIX, row['id']), headers=headers))

        self.log_results()
        Label(self.statusLabelFrame, text=grequests.map(response)).pack()

        return False

    def log_results(self):
        logging.basicConfig(filename=self.LOG_FILENAME % (self.DOMAIN_PREFIX), level=logging.DEBUG)

        logging.debug('This message should go to the log file')


root = Tk()

root.title("Vend Backend Tools")

app = GUI(root)

root.mainloop()
