/*
 *  Copyright © 2008, Matthias Urlichs <matthias@urlichs.de>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License (included; see the file LICENSE)
 *  for more details.
 */

/*
 * This header defines a task queue for AVR.
 */

#include "local.h"

#include <stdlib.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include "qtask.h"
#include "util.h"
#include "assert.h"

static task_head *head_now;
static task_head *tail_now;


void real_queue_task(task_head *task)
{
	//DBGS("Q %x",task);
	assert(!(SREG & _BV(SREG_I)),"queue_task from non-IRQ");
	assert(!task->next,"Queue Ouch1");
	assert(!task->delay,"Queue Delay");
	assert(tail_now != task,"Queue Ouch2");
#if 0 /* def ASSERTIONS */
	if((unsigned short)task->proc >= 0x4000) {
		cli();
		printf_P(PSTR("TaskPtr %x %s %x"),task,&task->proc,__builtin_return_address(0));
		report_error("Ouch");
	}
#endif
	assert((unsigned short)task->proc < 0x4000,"Invalid task pointer");

	if(tail_now) {
		assert(head_now,"Queue broken1");
		tail_now->next = task;
	} else {
		assert(!head_now,"Queue broken2");
		head_now = task;
	}
	tail_now = task;
	task->delay = TASK_MAGIC;
}

void dequeue_task(task_head *task)
{
	/* This should, ideally, never happen. */
	/* Therefore, blocking IRQs while running this is OK. */

	unsigned char sreg = SREG;
	task_head *th;

	cli();
	if(!task->delay)
		goto out;
#if 0
	if(task->delay != TASK_MAGIC) {
		dequeue_task_later(task);
		goto out;
	} 
#endif
	assert(task->delay == TASK_MAGIC, "DeQ delayed");

	if(head_now == task) {
		head_now = NULL;
		tail_now = NULL;
		assert(!task->next, "DeQ TaskNextSet");
	} else {
		th = head_now;
		assert(th, "DeQL TaskListEmpty");
		while(th->next != task) {
			assert(th->next, "DeQ TaskNotFound");
			th = th->next;
		}
	}
	task->delay = 0;
out:
	SREG = sreg;
}

/* return 1 if something was done */
unsigned char
run_tasks(void)
{
	cli();
	task_head *task = head_now;
	if(!task) {
		sei();
		return 0;
	}
	//sei();

	while(task) {
		//cli();
		task_head *tn = task->next;
		if (task == tail_now) {
			//DBGS("TaskQ1 %x %x  %x %x",task,tn,head_now,tail_now);
			head_now = NULL;
			tail_now = NULL;
			assert(!tn, "TaskQ1");
		} else {
			//DBGS("TaskQ2 %x %x  %x %x",task,tn,head_now,tail_now);
			assert(tn, "TaskQ2");
		}
		//DBGS("R %x %x",task,task->proc);
		task->delay = 0;
		task->next = NULL;
		sei();
		(*task->proc)(task);
		cli();
		//DBG("Rdone");
		task = tn;
	}
	sei();
	return 1;
}

