# # install python libraries
# from random import randrange
# from time import time
# from dataclasses import fields
# from random import random
# from time import sleep
# import logging
#
# # install Nebula modules
# from nebula.nebula_dataclass import NebulaDataClass
#
#
# class Affect:
#     """Accepts realtime data/ percept input from
#     human-in-the-loop e.g. live audio analysis,
#     skeletal tracking, joystick control.
#     By analysing the energy of input this class will
#     define which feed of the hivemind
#     (produced by the AI factory) to emit back to the client.
#     Like a thought train it is affected by the energy of a
#     percept, and duration of such listening."""
#
#     def __init__(self,
#                  dobot_commands_queue,
#                  hivemind: NebulaDataClass,
#                  speed: int = 1
#                  ):
#
#         print('Starting the Affect module')
#
#         # names for affect listening
#         self.stream_list = ['user_in',
#                             'rnd_poetry',
#                             'affect_net',
#                             'self_awareness']
#
#         # set running vars
#         # self.affect_logging = False
#         self.running = True
#         self.global_speed = speed
#
#         # own the dataclass
#         self.hivemind = hivemind
#
#         # Emission list is the highest level comms back to client
#         self.dobot_commands_queue = dobot_commands_queue
#         self.live_emission_data = 1
#
#         # little val for emission control avoiding repeated vals (see below)
#         self.old_val = 0
#
#     def thought_train(self):
#         """Listens to the realtime incoming signal that is stored in the dataclass ("user_input")
#         and calculates an affectual response based on general boundaries:
#             HIGH - if input stream is LOUD (0.8+) then emit, smash a random fill and break out to Daddy cycle...
#             MEDIUM - if input energy is 0.3-0.8 then emit, a jump out of child loop
#             LOW - nothing happens, continues with cycles
#         """
#         # 1. daddy cycle: top level cycle lasting 6-26 seconds
#         while self.running:
#             # flag for breaking on big affect signal
#             self.interrupt_bang = True
#
#             # Top level calc master cycle before a change
#             master_cycle = (randrange(600, 2600) / 100) + self.global_speed
#             loop_end = time() + master_cycle
#
#             logging.debug('\t\t\t\t\t\t\t\t=========AFFECT - Daddy cycle started ===========')
#             logging.debug(f"                 interrupt_listener: started! Duration =  {master_cycle} seconds")
#
#             # 2. child cycle: waiting for interrupt  from master clock
#             while time() < loop_end:
#                 # calc rhythmic intensity based on self-awareness factor & global speed
#                 intensity = getattr(self.hivemind, 'self_awareness')
#                 logging.debug(f'////////////////////////   intensity =  {intensity}')
#
#                 rhythm_rate = (randrange(10,
#                                         80) / 100) # / self.global_speed  # round(((rhythm_rate / intensity) * self.global_speed), 2) # / 10  # rhythm_rate * self.global_speed
#                 # self.hivemind['rhythm_rate'] = rhythm_rate
#                 setattr(self.hivemind, 'rhythm_rate', rhythm_rate)
#                 logging.debug(f'////////////////////////   rhythm rate = {rhythm_rate}')
#
#                 # if a major break out then go to Daddy cycle and restart
#                 if not self.interrupt_bang:
#                     break
#
#                 logging.debug('\t\t\t\t\t\t\t\t=========Hello - child cycle 1 started ===========')
#
#                 # randomly pick an input stream for this cycle
#                 # either user_in, random, net generation or self-awareness
#                 rnd = randrange(4)
#                 self.rnd_stream = self.stream_list[rnd]
#                 setattr(self.hivemind, 'affect_decision', self.rnd_stream)
#                 logging.debug(f'Random stream choice = {self.rnd_stream}')
#
#                 # hold this stream for 1-4 secs, unless interrupt bang
#                 end_time = time() + (randrange(1000, 4000) / 1000)
#                 logging.debug(f'end time = {end_time}')
#
#                 # 3. baby cycle - own time loops
#                 while time() < end_time:
#
#                     logging.debug('\t\t\t\t\t\t\t\t=========Hello - baby cycle 2 ===========')
#
#                     # make the master output the current value of the affect stream
#                     # 1. go get the current value from dict
#                     thought_train = getattr(self.hivemind, self.rnd_stream)
#                     logging.info(f'Affect stream current input value from {self.rnd_stream} == {thought_train}')
#
#                     # 2. send to Master Output
#                     setattr(self.hivemind, 'master_output', thought_train)
#                     logging.info(f'\t\t ==============  thought_train output = {thought_train}')
#
#                     # 3. emit to the client at various points in the affect cycle
#                     self.emitter(thought_train)
#
#                     ###############################################
#                     #
#                     # test realtime input against the affect matrix
#                     # behave as required
#                     #
#                     ###############################################
#
#                     # 1. get current mic level
#                     peak = getattr(self.hivemind, "user_in")
#                     logging.debug(f'testing current mic level for affect = {peak}')
#
#                     # 2. calc affect on behaviour
#                     # LOUD
#                     # if input stream is LOUD then smash a random fill and break out to Daddy cycle...
#                     if peak > 0.8:
#                         logging.debug('interrupt > HIGH !!!!!!!!!')
#
#                         # A - refill dict with random
#                         self.random_dict_fill()
#
#                         # B - jumps out of this loop into daddy
#                         self.interrupt_bang = False
#
#                         # C - interrupt Queue
#                         self.dobot_commands_queue.get()
#                         # self.dobot_commands_queue.put(peak)
#
#                         # D- break out of this loop, and next (cos of flag)
#                         break
#
#                     # MEDIUM
#                     # if middle loud fill dict with random, all processes norm
#                     elif 0.3 < peak < 0.8:
#                         logging.debug('interrupt MIDDLE -----------')
#
#                         # A. jumps out of current local loop, but not main one
#                         break
#
#                     # LOW
#                     # nothing happens here
#                     elif peak <= 0.3:
#                         logging.debug('interrupt LOW ----------- no action')
#
#                     # # get current rhythm_rate from hivemind
#                     # rhythm_rate = getattr(self.hivemind, 'rhythm_rate')
#
#                     # and wait for a cycle
#                     sleep(rhythm_rate)
#
#                 # and wait for a cycle
#                 sleep(rhythm_rate)
#
#             # and wait for a cycle
#             sleep(rhythm_rate)
#
#     def emitter(self, thought_train):
#         # if thought_train != self.old_val:
#             # self.emission_list.append(incoming_affect_listen)
#             # self.live_emission_data = incoming_affect_listen
#         self.dobot_commands_queue.put(thought_train)
#
#         logging.debug(f'AFFECT:                                EMITTING value {self.live_emission_data}')
#         self.old_val = thought_train
#
#     def random_dict_fill(self):
#         """Fills the working dataclass with random values. Generally called when
#         affect energy is highest"""
#         for field in fields(self.hivemind):
#             # print(field.name)
#             rnd = random()
#             setattr(self.hivemind, field.name, rnd)
#         logging.debug(f'Data dict new random values are = {self.hivemind}')
#
#     def quit(self):
#         self.running = False
