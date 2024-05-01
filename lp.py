import pandas
from pulp import *
import math
import datetime




def save_time(t):
	with open("times.txt", "a+") as myfile:
		myfile.write(str(t)+"\n")

def save_num_HHs_ppl(n_hh, n_ppl):
	with open("times.txt", "a+") as myfile:
		myfile.write("#HHs = %s ---- #Ppl = %s\n" %(n_hh, n_ppl))

def save_tot_L1_err(err):
	with open("times.txt", "a+") as myfile:
		myfile.write("Error = %s\n" %(err))




def no_agep(relp_val, sex_val, type_of_tuples, n_men):
	n_men_women = len(type_of_tuples)

	n_women = n_men_women-n_men
	row = [0]*n_men_women

	if relp_val == -1 and sex_val == -1:									# Use all vars
		row = [1]*n_men_women
		return row
	elif sex_val != -1 and sex_val[0] == 1:									# Which men?
		if relp_val == -1:													# No RELP => All men
			row = [1]*n_men
			row.extend([0]*n_women)
		else:																# Only those with given RELP
			for j in range(n_men):
				if type_of_tuples[j][1] == relp_val[0]:
					row[j] = 1
		return row
	elif sex_val != -1 and sex_val[0] == 2:									# Which women?
		if relp_val == -1:													# No RELP => All women
			row = [0]*n_men
			row.extend([1]*n_women)
		else:																# Only those with given RELP
			for j in range(n_men, n_men_women):
				if type_of_tuples[j][1] == relp_val[0]:
					row[j] = 1
		return row
	elif sex_val == -1 and relp_val != -1:									# Which relp? (Both men and women)
		for j in range(n_men_women):
			if type_of_tuples[j][1] == relp_val[0]:
				row[j] = 1
		return row


def helper_given_agep_men(agep_val, type_of_tuples, u, row, given_relp, relp_val):
	for j in range(u):
		if type_of_tuples[j][0][0] >= agep_val[0] and type_of_tuples[j][0][1] <= agep_val[1] and \
			(not given_relp or type_of_tuples[j][1] == relp_val[0]):
			row[j] = 1
		elif type_of_tuples[j][0][0] > agep_val[1]:
			break
	return row

def helper_given_agep_women(agep_val, type_of_tuples, l, u, row, given_relp, relp_val):
	for j in range(l, u):
		if type_of_tuples[j][0][0] >= agep_val[0] and type_of_tuples[j][0][1] <= agep_val[1] and \
			(not given_relp or type_of_tuples[j][1] == relp_val[0]):
			row[j] = 1
		elif type_of_tuples[j][0][0] > agep_val[1]:
			break
	return row

def given_agep(agep_val, relp_val, sex_val, type_of_tuples, n_men):
	n_men_women = len(type_of_tuples)

	n_women = n_men_women-n_men
	row = [0]*n_men_women

	if relp_val == -1 and sex_val == -1:										# Use all vars with age in specified range
		# Check for both men and women
		row = helper_given_agep_men(agep_val, type_of_tuples, n_men, row, False, relp_val)
		return helper_given_agep_women(agep_val, type_of_tuples, n_men, n_men_women, row, False, relp_val)
	elif sex_val != -1 and sex_val[0] == 1:										 # Which men?
		if relp_val == -1:
			return helper_given_agep_men(agep_val, type_of_tuples, n_men, row, False, relp_val)
		else:
			return helper_given_agep_men(agep_val, type_of_tuples, n_men, row, True, relp_val)
	elif sex_val != -1 and sex_val[0] == 2:
		if relp_val == -1:
			return helper_given_agep_women(agep_val, type_of_tuples, n_men, n_men_women, row, False, relp_val)
		else:
			return helper_given_agep_women(agep_val, type_of_tuples, n_men, n_men_women, row, True, relp_val)
	elif sex_val == -1 and relp_val != -1:
		row = helper_given_agep_men(agep_val, type_of_tuples, n_men, row, True, relp_val)
		return helper_given_agep_women(agep_val, type_of_tuples, n_men, n_men_women, row, True, relp_val)








def get_existing_tuple_types(R1):
	type_of_tuples = []

	distinct_p = R1.drop_duplicates()
	distinct_p = distinct_p.sort_values(['sex', 'agep', 'relp'], ascending=[True, True, True])
	for i in distinct_p.index.tolist():
		row = distinct_p.loc[i]
		type_of_tuples.append([row['agep'], row['relp'], row['sex']])
	return type_of_tuples








def get_counts_augment_R1_3way(S_CC, agep_intervals_used_in_S_CC, relp_used_in_S_CC, sex_used_in_S_CC, num_R1_non_key_attrs, persons):
	aug_q = []
	aug_counts = []

	# for constraint in S_CC: use constraint[:3] to track combos of AGEP-RELP-SEX values to use when augmenting S_CC
	combos = []
	for constraint in S_CC:
		k = constraint[:num_R1_non_key_attrs]
		if k not in combos:
			combos.append(k)

			agep_vals = [k[0]]
			if k[0] == -1:
				agep_vals = agep_intervals_used_in_S_CC						# [[l_1, u_1], [l_2, u_2], ...]

			relp_vals = k[1]
			if k[1] == -1:
				relp_vals = relp_used_in_S_CC								# attr_intervalization[1]

			sex_vals = k[2]
			if k[2] == -1:
				sex_vals = sex_used_in_S_CC									# attr_intervalization[2]

			print("\n%s" %(k))
			for a1 in agep_vals:
				for a2 in relp_vals:
					for a3 in sex_vals:
						q = [a1, [a2], [a3], -1, -1]
						if q not in aug_q:
							aug_q.append(q)
							print("\t%s" %(aug_q[-1]))
	for tup in aug_q:
		l = persons[(persons['agep'] >= tup[0][0]) & (persons['agep'] <= tup[0][1]) & \
			(persons['relp'] == tup[1][0]) & (persons['sex'] == tup[2][0])]
		aug_counts.append(l.shape[0])
	return aug_q, aug_counts








def main(col_R1, col_R2, S_CC, b_S_CC, persons, housing, V1, output_filename):
	io_stats = open(output_filename, "a")

	io_stats.write("Algo 1.2 ---- start time %s\n" %(datetime.datetime.now()))
	for i in range(len(S_CC)):
		io_stats.write("\t%5d %s\n" %(b_S_CC[i], S_CC[i]))
	io_stats.write("\n\tCCs to Ax=b ---- start time %s\n" %(datetime.datetime.now()))
	save_time(datetime.datetime.now())


	num_CCs = len(S_CC)


	''' ----------------------------------------------- List vars ------------------------------------------------ '''
	attr_intervalization = [[] for i in range(len(col_R1) + len(col_R2))]

	type_of_tuples = []
	num_types = 0
	n_men = 0
	n = 0

	n_age = 0
	n_ten = 0
	n_puma = 0

	aug_q = []
	aug_counts = []

	A = []

	''' --------------------------------------------------------------------------------------------------------------
									Get attr_intervalization for attributes in R1
	-------------------------------------------------------------------------------------------------------------- '''
	# 1. Store breaking points from the domain of attributes used in S_CC
	for constraint in S_CC:
		for i in range(len(col_R1)):
			if constraint[i] != -1:
				for j in range(len(constraint[i])):
					val = constraint[i][j]
					if j == 1:
						val += 1							# [0, 17] makes list [0, 18] for [0, 18), [18, ...)
					if val not in attr_intervalization[i]:
						attr_intervalization[i].append(val)
	# 2. Sort and adjust AGEP's intervals
	for i in range(len(col_R1)):
		attr_intervalization[i].sort()
		if i == 0:											# AGEP domain is [0, 114]
			if 0 not in attr_intervalization[i]:
				l = [0]
				l.extend(attr_intervalization[i])
				attr_intervalization[i] = l
			if 115 not in attr_intervalization[i]:
				attr_intervalization[i].append(115)
	n_age = len(attr_intervalization[0])

	# Mark which intervals given by AGEP's intervalization are used in S_CC
	agep_intervals_used_in_S_CC = []
	if n_age == 2:											# No AGEP value or [0, 114] specified in S_CC
		agep_intervals_used_in_S_CC.append([0, 114])
	else:
		for i in range(n_age - 1):
			age = attr_intervalization[0][i]
			next_age = attr_intervalization[0][i+1]
			for constraint in S_CC:
				if (constraint[0] != -1 and age >= constraint[0][0] and age <= constraint[0][1]) and ([age, next_age - 1] not in agep_intervals_used_in_S_CC):
					agep_intervals_used_in_S_CC.append([age, next_age - 1])
					break
	print("\n\nAGEP intervals (post intervalization) that are used in the input set of CCs: %s\n\n" %(agep_intervals_used_in_S_CC))


	''' --------------------------------------------------------------------------------------------------------------
							Get tuple types and merge using attrs that allow intervals in S_{CC}
	-------------------------------------------------------------------------------------------------------------- '''
	type_of_tuples = get_existing_tuple_types(persons)
	print("\nType of tuples before binning by intervals = %s" %(len(type_of_tuples)))
	io_stats.write("\t\tType of tuples before binning by intervals = %s\n" %(len(type_of_tuples)))

	# Update the agep value to the corresponding interval from agep intervalization
	first_woman = False
	i = 0
	for tup in type_of_tuples:
		if tup[2] == 2 and not first_woman:
			i = 0
			first_woman = True
		u = attr_intervalization[0][i+1]
		while tup[0] >= u:
			i += 1
			u = attr_intervalization[0][i+1]
		l = attr_intervalization[0][i]
		u = attr_intervalization[0][i+1]
		#print(l, "\t", u, "\t", [l, u-1], "\t", tup)
		tup[0] = [l, u-1]
	# Remove duplicates below
	no_dup = []
	for tup in type_of_tuples:
		if tup not in no_dup:
			no_dup.append(tup)
			if tup[2] == 1:
				n_men += 1
			#print(no_dup[-1])
	type_of_tuples = no_dup
	num_types = len(type_of_tuples)
	print("Number of tuple types in R1 (using AGEP intervalization) = %s" %(num_types))
	io_stats.write("\t\tNumber of tuple types in R1 (using AGEP intervalization) = %s\n" %(num_types))
	n = num_types


	''' --------------------------------------------------------------------------------------------------------------
							Get active domain for attributes in R2, and total number of vars in IP
	-------------------------------------------------------------------------------------------------------------- '''
	# Once we know the distinct values in TEN and PUMA10 (from S_{CC}), calculate number of variables
	# agep, relp, sex, ten, puma10
	if len(attr_intervalization[1]) == 0:				# No RELP value used in S_CC
		attr_intervalization[1] = persons['relp'].drop_duplicates().tolist()
		attr_intervalization[1].sort()

	if len(attr_intervalization[2]) == 0:				# No SEX value used in S_CC
		attr_intervalization[2] = persons['sex'].drop_duplicates().tolist()
		attr_intervalization[2].sort()

	attr_intervalization[3] = housing['ten'].drop_duplicates().tolist()
	attr_intervalization[3].sort()
	n_ten = len(attr_intervalization[3])
	if n_ten > 0:
		n = n * n_ten

	attr_intervalization[4] = housing['puma10'].drop_duplicates().tolist()
	attr_intervalization[4].sort()
	n_puma = len(attr_intervalization[4])
	if n_puma > 0:
		n = n * n_puma

	print("\t\tDistinct values (TEN, PUMA10):\t%s\n\t\t%s\n" %(attr_intervalization[3], attr_intervalization[4]))
	print("Number of variables = %s" %(n))
	io_stats.write("\n\t\tNumber of variables = %2d\n" %(n))


	''' --------------------------------------------------------------------------------------------------------------
								Augment S_{CC} using 3-way (AGEP-RELP-SEX) marginal from R1
	-------------------------------------------------------------------------------------------------------------- '''
	aug_q, aug_counts = get_counts_augment_R1_3way(S_CC, agep_intervals_used_in_S_CC, attr_intervalization[1], \
						attr_intervalization[2], len(col_R1), persons)
	aug_q.extend(S_CC)
	aug_counts.extend(b_S_CC)


	''' --------------------------------------------------------------------------------------------------------------
							Use S_CC and add the corresponding x_i's to populate rows in A and b
	-------------------------------------------------------------------------------------------------------------- '''
	for i in aug_q:
		#print(i)
		row = []

		if i[4] != -1:
			idx_puma = attr_intervalization[4].index(i[4][0])
			row = [0]*num_types*n_ten*idx_puma

		if i[0] == -1:
			row_sub = no_agep(i[1], i[2], type_of_tuples, n_men)
			#print(len(row_sub), "\t", row_sub)
		else:
			row_sub = given_agep(i[0], i[1], i[2], type_of_tuples, n_men)
			#print(len(row_sub), "\t", row_sub)

		if i[3] == -1:
			row.extend(row_sub*n_ten)
		elif i[3][0] == 1:
			row.extend(row_sub)
			if n_ten >= 2:
				row.extend([0]*int(n/(n_puma*n_ten) * (n_ten-1)))			   # Ignore other TENs
		elif i[3][0] == 2:
			row.extend([0]*int(n/(n_puma*n_ten)))
			row.extend(row_sub)
			if n_ten >= 3:
				row.extend([0]*int(n/(n_puma*n_ten) * (n_ten-2)))			   # Ignore other TENs
		elif i[3][0] == 3:
			row.extend([0]*int(2*n/(n_puma*n_ten)))
			row.extend(row_sub)
			if n_ten == 4:
				row.extend([0]*int(n/(n_puma*n_ten)))						   # Ignore other TENs ... n_ten - 3 is 1 here
		elif i[3][0] == 4:
			row.extend([0]*int(3*n/(n_puma*n_ten)))
			row.extend(row_sub)

		if i[4] != -1:
			num_pumas_rem = n_puma - attr_intervalization[4].index(i[4][0]) - 1
			row.extend([0]*int(n/n_puma)*num_pumas_rem)
		else:
			row.extend(row*(n_puma-1))

		A.append(row)
		#print(len(A[-1]))
		#print("----")

	print("\nSolving IP ....")
	prob = LpProblem("myProblem", LpMinimize)
	ppl_types = [i for i in range(n)]

	ppl_vars = LpVariable.dicts("person", ppl_types, lowBound=0, cat='Integer')
	#print(ppl_vars)

	prob += 0

	for i in range(len(A)):
		prob += lpSum([A[i][j]*ppl_vars[j] for j in ppl_types]) == aug_counts[i], "CC"+str(i)

	status = prob.solve()
	io_stats.write("\t\t******** STATUS = %s\n" %(LpStatus[prob.status]))
	print("\t\t******** STATUS = %s\n" %(LpStatus[prob.status]))

	x = [0 for i in range(n)]
	for v in prob.variables():
		#print(v.name, "=", v.varValue)
		if v.name != '__dummy':
			x[int(v.name.split("_")[1])] = int(v.varValue)
	#io_stats.write(str(x)+"\n")

	io_stats.write("\tCCs to Ax=b ---- end time %s\n\n" %(datetime.datetime.now()))
	save_time(datetime.datetime.now())
	

	io_stats.write("\tAx=b to V1 ---- start time %s\n" %(datetime.datetime.now()))
	save_time(datetime.datetime.now())

	# Create UPDATE queries to run on V_1 in PostgreSQL on the basis of x. We know the values x[i]'s encode.
	# AGEP, RELP, SEX, TEN, PUMA10
	for p in range(len(attr_intervalization[4])):
		for t in range(len(attr_intervalization[3])):
			for i in range(num_types):
				x_i_val = x[p*n_ten*num_types + t*num_types + i]
				if x_i_val > 0:
					agep_val = type_of_tuples[i][0]
					relp_val = type_of_tuples[i][1]
					sex_val = type_of_tuples[i][2]
					ten_val = attr_intervalization[3][t]
					puma_val = attr_intervalization[4][p]

					l = V1[(V1['agep'] >= agep_val[0]) & (V1['agep'] <= agep_val[1]) & \
						(V1['relp'] == relp_val) & (V1['sex'] == sex_val) & (V1['ten'] == -1) & (V1['puma10'] == -1)]
					if x_i_val < l.shape[0]:
						l = l[0:x_i_val]
					# UPDATE
					for p_id in l.index.tolist():
						V1.loc[p_id]['ten'] = ten_val
						V1.loc[p_id]['puma10'] = puma_val
					#l['ten'] = [ten_val]*l.shape[0]							# We know these vals are +ve ints
					#l['puma10'] = [puma_val]*l.shape[0]

					print(x_i_val, "\t", [agep_val, [relp_val], [sex_val], [ten_val], [puma_val]])
	#cursor.execute("SELECT COUNT(*) FROM V1 WHERE PUMA10=-1 OR TEN = -1")
	#print("\n\nNumber of tuples with missing/incomplete V1 assignment = %s\n\n" %(cursor.fetchone()[0]))

	io_stats.write("\tAx=b to V1 ---- end time %s\n\n" %(datetime.datetime.now()))

	# CHECK CC VIOLATIONS FOR CCs
	err = 0
	for k in range(num_CCs):
		cc = S_CC[k]
		target_count = b_S_CC[k]

		l = V1
		for i in range(len(col_R1)):
			if cc[i] != -1:
				if i == 0:														# range or interval
					l = l[(l[col_R1[i]] >= cc[i][0]) & (l[col_R1[i]] <= cc[i][1])]
				else:															# categorical
					l = l[l[col_R1[i]] == cc[i][0]]
		for j in range(len(col_R2)):
			if cc[i+1+j] != -1:													# categorical
				l = l[l[col_R2[j]] == cc[i+1+j][0]]
		ans = l.shape[0]

		if target_count != ans:
			if err == 0:
				io_stats.write("\tCCs with target counts minus counts in V1\n")
			io_stats.write("%5d - %5d = %5d \t%s\n" %(target_count, ans, target_count - ans, cc))
			err += abs(target_count - ans)
	
	io_stats.write("Algo 1.2 ---- end time %s\n" %(datetime.datetime.now()))
	save_time(datetime.datetime.now())
	save_tot_L1_err("%s\n" %(err))
	
	
	io_stats.write("----------------------------------------------------------------------------\n\n\n\n\n")
	io_stats.close()
	return V1




if __name__ == '__main__':
	main(col_R1, col_R2, S_CC, b_S_CC, persons, housing, V1, output_filename)