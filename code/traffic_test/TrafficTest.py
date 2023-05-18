import time, datetime
import os
import json
from multiprocessing import Process
import argparse
import epics, pvaccess


# 结果汇总成.json文件，格式: (time)-traffic-test.json
def json_process(tag, delete=True):
    ls = os.listdir()
    json_data = []
    for file_name in ls:
        if f'{tag}-' in file_name:
            with open(file_name, 'r') as f:
                json_data.append(json.load(f))
    if json_data:
        result = {'result': [], 'test_info': json_data[0]['test_info']}
        for item in json_data:
            temp = item['result']
            for res_item in temp:
                result['result'].append(res_item)
        with open(f'{tag}-traffic-test.json', 'w') as f:
            json.dump(result, f)
    if delete:
        for file_name in ls:
            if f'{tag}-' in file_name:
                os.remove(file_name)


class Test_Class:
    def __init__(self, tag='UndefinedTest'):
        self._flag = False
        self.tag = tag
        self.count = 0
        self.error_count = 0
        self._temp_value = None
        self._value = None
        self._start_value = None
        self._stop_value = None

    def value_callback_pyepics(self, **kwargs):
        self._temp_value = kwargs['value']
        if self._flag:
            temp = self._temp_value - self._value - 1
            if temp > 0:
                self.error_count += temp
            self._value = self._temp_value
            # print(self.error_count)

    def value_callback_pvapy(self, pv):
        self._temp_value = pv['value']
        if self._flag:
            temp = self._temp_value - self._value - 1
            if temp > 0:
                self.error_count += temp
            self._value = self._temp_value

    def start(self):
        self._flag = True
        self._value = self._temp_value
        self._start_value = self._temp_value

    def stop(self):
        self._flag = False
        self._stop_value = self._temp_value
        self.count = self._stop_value - self._start_value

    def __str__(self):
        return f'Test_Class("{self.tag}") with {int(self.error_count)}/{int(self.count)} error/total'


# 单个进程执行的测试程序
# test_type: 测试类型, record_num: 要测试的远端Record数量, client_num: 生成的连接测试客户端数量,
# protocol_type: 测试协议类型 ['ca', 'pva']
# verbose: 显示详细信息, test_info: 附加的测试信息
def run_test(record_list: list, client_num, test_duration, protocol_type='ca', verbose=True, test_info: dict = None):
    Connect_Timeout_Retry_Times = 5
    pid = os.getpid()

    record_num = len(record_list)
    pv_list = []
    test_list = []

    for i in range(0, client_num):
        temp_tc = Test_Class(str(pid) + f'-{i}:{record_list[i % record_num]}')
        if protocol_type.lower() == 'ca':
            temp_pv = epics.PV(record_list[i % record_num], callback=temp_tc.value_callback_pyepics)
        else:  # 'pva'
            temp_pv = pvaccess.Channel(record_list[i % record_num])
            temp_pv.monitor(temp_tc.value_callback_pvapy, 'field(value,alarm,timeStamp)')
        test_list.append(temp_tc)
        pv_list.append(temp_pv)

    ready_flag = False
    for i in range(0, Connect_Timeout_Retry_Times):
        print(f'Test pid {pid}: Connecting to PVs... ')
        if protocol_type.lower() == 'ca':
            temp = [pv_item.connected for pv_item in pv_list]
        else:  # 'pva'
            temp = [pv_item.isConnected() for pv_item in pv_list]
        if all(temp):
            ready_flag = True
            break
        else:
            time.sleep(1)
    if ready_flag:
        print(f'Test pid {pid}: All PV connected. Start testing... ')
        for t in test_list:
            t.start()
        time.sleep(test_duration)
        for t in test_list:
            t.stop()
        print(f'Test pid {pid}: Test finished. ')

        if verbose:
            for t in test_list:
                print(t)

        result = [[item.tag, item.error_count, item.count] for item in test_list]
        if test_info:
            test_info['client_num'] = client_num
            test_info['test_duration'] = test_duration
            test_info['pv'] = record_list
            if protocol_type == 'ca':
                test_info['test_protocol'] = 'ca-pyepics'
            else:
                test_info['test_protocol'] = 'pva-pvapy'
            test_info['date'] = str(datetime.date.today())
        res = {'result': result, 'test_info': test_info}

        tag = test_info.get('tag')
        if tag:
            with open(f'{tag}-{pid}.json', 'w') as f:
                json.dump(res, f)
        else:
            with open('test.json', 'w') as f:
                json.dump(res, f)

    else:
        print(f'Test pid {pid}: Connection timeout. ')


if __name__ == '__main__':
    # argparse part
    Process_Default = 1
    Duration_Default = 10

    parser = argparse.ArgumentParser(
        description='PV通信测试脚本(For single value pv). 依赖的第三方库: pyepics, pvapy. ')
    parser.add_argument('pv_list', metavar='pv list', type=str, nargs='+',
                        help='PV list for test. ')
    parser.add_argument('-c', '--client', type=int, default=0,
                        help='Client number for connecting test PV, for invalid input use default. Default value equals to the length of PV list. ')
    parser.add_argument('-t', '--duration', type=int, default=Duration_Default, help='Test duration. ')
    parser.add_argument('-p', '--process', type=int, default=Process_Default,
                        help='Number of process created for repeating test. ')
    parser.add_argument('-v', '--verbose', action="store_true", help='Print details. ')
    parser.add_argument('--pva', action="store_true", help='Use PVAccess. ')
    args = parser.parse_args()

    pv_list = args.pv_list
    Verbose = args.verbose
    if args.pva:
        Protocol_Type = 'pva'
    else:
        Protocol_Type = 'ca'
    if args.process <= 0:
        print(f'Invalid input for parameter "process", use default value: {Process_Default}. ')
        N_Process = Process_Default
    else:
        N_Process = args.process
    if args.duration <= 0:
        print(f'Invalid input for parameter "duration", use default value: {Duration_Default}. ')
        Time_Test = Duration_Default
    else:
        Time_Test = args.duration
    if args.client < len(args.pv_list):
        print(f'Invalid input for parameter "client", use default value equals to length of PV list: {len(args.pv_list)}. ')
        N_Client = len(args.pv_list)
    else:
        N_Client = args.client

    run_flag = None
    while True:
        res = input(
            f'Run test creating {N_Process} process(es) each with parameters: pv_list={pv_list}, N_Client={N_Client}, '
            f'Time_Test={Time_Test}, Protocol_Type={Protocol_Type}, Verbose={Verbose}?|[y/n]')
        if res.lower() == 'yes' or res.lower() == 'y':
            run_flag = True
            break
        elif res.lower() == 'no' or res.lower() == 'n':
            run_flag = False
            break

    # test part
    if run_flag:

        test_tag = int(time.time())
        info = {'tag': test_tag}

        process_list = []
        for i in range(0, N_Process):
            process_list.append(
                Process(target=run_test, args=(pv_list, N_Client, Time_Test, Protocol_Type, Verbose, info)))
        for p in process_list:
            p.start()
        for p in process_list:
            p.join()
        json_process(test_tag)
