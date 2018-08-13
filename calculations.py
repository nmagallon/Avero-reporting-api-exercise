import requests
from datetime import datetime, timedelta

class Calculations(): 

	def __init__(self, token):
		self.api_source ='https://secret-lake-26389.herokuapp.com/'
		self.token = token
		# cache structure: {business_id: labor: [{labor1}, {labor2}, ...], items: [{item1}, {item2}, ...]}
		self. cache = {}

	def update_time_interval(self, start_interval, timeInterval):
		'''
		Takes a start time in datetime format and creates an end time that is 1 timeInterval away from the start time.
		'''
		if timeInterval=='hour':
			end_interval = start_interval+timedelta(hours=1)
		elif timeInterval=='day':
			end_interval = start_interval+timedelta(days=1)
		elif timeInterval=='week':
			end_interval = start_interval+timedelta(weeks=1)
		elif timeInterval=='month':
			end_interval = start_interval+timedelta(days=30)
		return end_interval

	def update_cache(self, business_id, get_entries, category):
		'''
		Updates the cache for a given business_id and updates the category in the cache.
		Returns True if the update was sucessful, otherwise False
		'''
		try:
			visit_all_entries = False
			offset = 0
			while not visit_all_entries:
				request = self.api_source + get_entries + '?business_id={0}&limit=500&offset={1}'.format(business_id,offset)
				entries = requests.get(request, headers={'Authorization':self.token}).json()
				# takes the new data results and adds them to the end of the cached list
				self.cache[business_id][category].extend(entries['data'])
				offset += 500 
				if offset >= entries['count']:
					visit_all_entries = True
			print "updated cache: " + str(len(self.cache[business_id][category])) + " new entries added"
			return True
		except:
			return False

	def LCP(self, business_id, report, timeInterval, start, end):
		'''
		Labor Cost Percentage = Labor / Sales
		'''
		# Check if search has previously been done
		if business_id not in self.cache:
			self.cache[business_id] = {'items': [], 'labor': []}
		if len(self.cache[business_id]['labor']) == 0:
			cache_updated = self.update_cache(business_id, 'laborEntries', 'labor')
			if not cache_updated:
				return "There was a problem with the request. Please check that the query is correct."
		if len(self.cache[business_id]['items']) == 0:
			cache_updated = self.update_cache(business_id, 'orderedItems', 'items')
			if not cache_updated:
				return "There was a problem with the request. Please check that the query is correct."

		# Create output
		output = {"report": report,  "timeInterval": timeInterval, "data": []}

		# Iterate over the timesteps to get all labor costs (wage * hours worked in range) and sales
		start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
		end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
		start_interval = start_time
		end_interval = self.update_time_interval(start_interval, timeInterval)
		while end_interval <= end_time:
			item_prices = 0.0
			labor_costs = 0.0
			# Find corresponding items
			for item in self.cache[business_id]['items']:
				created = datetime.strptime(item['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ') 
				# Make sure item creation falls within the timestep 
				if created >= start_interval and created < end_interval:
					item_prices += item['price']
			# Find corresponding labor 
			for labor in self.cache[business_id]['labor']:
				clock_in = datetime.strptime(labor['clock_in'],'%Y-%m-%dT%H:%M:%S.%fZ')
				clock_out = datetime.strptime(labor['clock_out'],'%Y-%m-%dT%H:%M:%S.%fZ')
				if (clock_in >= start_interval and clock_in < end_interval) or (clock_out > start_interval and clock_out<= end_interval) or (clock_in < start_interval and clock_out > end_interval):
					# calculate the hours worked in the timestep and multiply by the pay rate
					pay_rate = labor['pay_rate']
					start_pay = max(clock_in, start_interval)
					end_pay = min(clock_out, end_interval)
					work_shift = end_pay - start_pay
					work_hours = work_shift.total_seconds()/3600.0
					labor_costs += work_hours*pay_rate
			# Calculate output
			if item_prices>0:
				value = (labor_costs/item_prices)*100.0
			else:
				value = 0
			output['data'].append({'timeFrame': {'start': str(start_interval), 'end':str(end_interval)}, 'value': value})
			# Update time interval for next iteration
			start_interval = end_interval
			end_interval = self.update_time_interval(start_interval, timeInterval)
		return output


	def FCP(self, business_id, report, timeInterval, start, end):
		'''
		Food Cost Percentage = Item Cost / Selling Prices
		'''
		# Check if busines is in cache and if not, update cache
		if business_id not in self.cache:
			self.cache[business_id] = {'items': [], 'labor': []}
		if len(self.cache[business_id]['items']) == 0:
			cache_updated = self.update_cache(business_id, 'orderedItems', 'items')
			if not cache_updated:
				return "There was a problem with the request. Please check that the query is correct."

		# Create output
		output = {"report": report,  "timeInterval": timeInterval, "data": []}

		# Calculate total item costs and total selling prices for each timestep
		start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
		end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
		start_interval = start_time
		end_interval = self.update_time_interval(start_interval, timeInterval)
		while end_interval <= end_time:
			item_costs = 0.0
			item_prices = 0.0
			#Find corresponding items
			for item in self.cache[business_id]['items']:
				created = datetime.strptime(item['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ') 
				# Make sure item creation falls within the timestep 
				if created >= start_interval and created < end_interval:
					item_costs += item['cost']
					item_prices += item['price']
			if item_prices>0:
				value = (item_costs/item_prices)*100.0
			else:
				value = 0
			output['data'].append({'timeFrame': {'start': str(start_interval), 'end':str(end_interval)}, 'value': value})
			# Update time interval for next iteration
			start_interval = end_interval
			end_interval = self.update_time_interval(start_interval, timeInterval)
		return output

	def EGS(self, business_id, report, timeInterval, start, end):
		'''
		Employee Gross Sales = Sum(Selling Prices)
		'''
		# Check if search has previously been done
		if business_id not in self.cache:
			self.cache[business_id] = {'items': [], 'labor': []}
		if len(self.cache[business_id]['labor']) == 0:
			cache_updated = self.update_cache(business_id, 'laborEntries', 'labor')
			if not cache_updated:
				return "There was a problem with the request. Please check that the query is correct."
		if len(self.cache[business_id]['items']) == 0:
			cache_updated = self.update_cache(business_id, 'orderedItems', 'items')
			if not cache_updated:
				return "There was a problem with the request. Please check that the query is correct."

		# Create output
		output = {"report": report,  "timeInterval": timeInterval, "data": []}
		
		# Iterate over the timesteps to get all sales for each employee that worked during that time. 
		start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
		end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ')
		start_interval = start_time
		end_interval = self.update_time_interval(start_interval, timeInterval)
		while end_interval <= end_time:
			# list of employees who worked during the timestep
			employees = []
			# Determine which employees were working during the timestep
			for labor in self.cache[business_id]['labor']:
				clock_in = datetime.strptime(labor['clock_in'],'%Y-%m-%dT%H:%M:%S.%fZ')
				clock_out = datetime.strptime(labor['clock_out'],'%Y-%m-%dT%H:%M:%S.%fZ')
				if (clock_in >= start_interval and clock_in < end_interval) or (clock_out > start_interval and clock_out<= end_interval) or (clock_in < start_interval and clock_out > end_interval):
					employees.append((labor['employee_id'], labor['name']))

			for employee in employees:
				employee_id, employee_name = employee[0], employee[1]
				sales = 0.0
				# Find items sold by employee during this timeframe
				for item in self.cache[business_id]['items']:
					if item['employee_id']==employee_id:
						created = datetime.strptime(item['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
						# Make sure item creation falls within the timestep 
						if (created >= start_interval and created < end_interval):
							sales += item['price']
				output['data'].append({'timeFrame': {'start': str(start_interval), 'end':str(end_interval)}, 'value': sales, 'employee':employee_name})
			# Update time interval for next iteration
			start_interval = end_interval
			end_interval = self.update_time_interval(start_interval, timeInterval)
		return output


