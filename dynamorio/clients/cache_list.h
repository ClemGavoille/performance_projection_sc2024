/* ******************************************************************************
 * Copyright (c) 2013-2016 Google, Inc.  All rights reserved.
 * Copyright (c) 2011 Massachusetts Institute of Technology  All rights reserved.
 * Copyright (c) 2008 VMware, Inc.  All rights reserved.
 * ******************************************************************************/

/*
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * * Redistributions of source code must retain the above copyright notice,
 *   this list of conditions and the following disclaimer.
 *
 * * Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimer in the documentation
 *   and/or other materials provided with the distribution.
 *
 * * Neither the name of Google, Inc. nor the names of its contributors may be
 *   used to endorse or promote products derived from this software without
 *   specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL GOOGLE, INC. OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
 * DAMAGE.
 */

#include "dr_api.h" /* for file_t, client_id_t */
#include <stdio.h>

#define MAX_DEPTH 700

typedef struct struct_cache_list {
	uint64_t address;
	struct struct_cache_list *prev;
	struct struct_cache_list *next;
} cache_list;

double binomial_coeff(int n, int k)
{
	double res = 1.0;
	if (k > n)
		return 0.0;
	for (int i = 1; i <= k; ++i)
		res = res * (n - k + i) / i;
	return res;
}

double binpow(double a, int b) {
	double res = 1.0;
	for (int i = 0; i < b; i++) {
		res = res * a;
	}
	return res;
}

void add(uint64_t address, cache_list** cache_level)
{

	cache_list *new_entry = (cache_list *)malloc(sizeof(cache_list));
	new_entry->address = address;
	new_entry->next = (*cache_level);
	new_entry->prev = NULL;
	if ((*cache_level) != NULL)
		(*cache_level)->prev = new_entry;
	(*cache_level) = new_entry;
}

/*Check if address is in the list and return value of stack distance */
int add_and_remove(uint64_t address, cache_list ** cache_level)
{
	int index = 0;
	cache_list *cursor = (*cache_level);
	while ( index < MAX_DEPTH )
	{
		if (cursor == NULL)
		{
			add(address,cache_level);
			return -1;
		}
		if (address == cursor->address)
		{
			if (cursor->prev != NULL) /*if there is no prev,it means it's the head, no change here and just return 0*/
				cursor->prev->next = cursor->next; /*replace in double linked list*/
			if (cursor->next != NULL)
				cursor->next->prev = cursor->prev;
			add(address,cache_level);
			//free(cursor);
			return index;
		}
		index++;
		cursor = cursor->next;
	}
	/* Here we haven't found the address and we got over the max_depth, so we add address to head AND remove last */
	add(address,cache_level);
	if (cursor->prev != NULL)
		cursor->prev->next = cursor->next;
	free(cursor);
	return -1;
}

