import time
import sys
sys.path.append('/Users/vincentl/PycharmProjects/Projects/xiaoheigong/')
import utils.email as email
import company


time_interval = 10  # seconds


def email_bug(bug, receivers):
        title = 'Xiaoheigong bug report'
        content = '<html><body>Hi,<br><p>There\'s a bug occurred:</p><p>'+ bug +'</p><br>-- Vincent Liu</body></html>'
        email.sendEmail(title, content, receivers)
        return True

def runner(time_interval):
    while 1:
        try:
            print('hello')  # replace to run scrapers
            time.sleep(time_interval)
            # raise Exception('hello')
        except Exception as e:
            try:
                email_bug(str(e), ['allenliux@163.com'])
            except:
                print('failed to send email')


if __name__ == '__main__':
    start_time = time.time()
    runner(time_interval)
    print('======= Time taken: %f =======' %(time.time() - start_time))