import pandas as pd
import numpy as np

def load_log(log_path):
    df = pd.DataFrame.from_csv(log_path, header=None)
    
    six_mov_ids_shown = ['mid_{}'.format(i) for i in range(1, 7)]
    six_tag_ids = ['tid_{}'.format(i) for i in range(1, 7)]
    six_tag_vals = ['tval_{}'.format(i) for i in range(1, 7)]
    
    df.columns = np.concatenate([six_mov_ids_shown, ["depth", "ch_mid"], six_tag_ids, six_tag_vals])
    df.index.names = ['uid']
    return lambda : df


def ideal_dcg(mini_session):
    mdf = mini_session
    fake_rank = [1 for _ in range(len(mdf))]
    return np.sum([(2**r - 1) / np.log(k + 2) for k, r in enumerate(fake_rank)])


def dcg(mini_session):
    mdf = mini_session
    return np.sum([(2**r - 1) / np.log(k + 2) for k, r in enumerate(mdf.new_rank)]) / ideal_dcg(mdf)


def session_gcd(df):
    depth = np.array(df.depth)
    n_zero = -1
    n_sess = np.array([0 for _ in range(len(depth))])

    for i in range(len(depth)):
        if depth[i] == 0:
            n_zero += 1
        n_sess[i] = n_zero

    df['n_sess'] = n_sess
    df.head()

    mini_sessions = [df[df.n_sess == i] for i in range(max(df.n_sess) + 1)]

    mini_dcgs = [dcg(mini_session) for mini_session in mini_sessions]
    mini_dcgs
    return np.mean(mini_dcgs)

def user_rank(x):
    mids = [x.mid_6, x.mid_5, x.mid_4, x.mid_3, x.mid_2, x.mid_1]
#     return mids.index(x.ch_mid) + 1 if x.ch_mid in mids else 0  
    return  1 if x.ch_mid in mids else 0  


# In[236]:

def log_gcd(log):

    log.ch_mid = log.ch_mid.shift(-1)
    df = log[:-1]

    new_rank = df.apply(user_rank, axis=1)
    df['new_rank'] = new_rank

    sessions = [df[df.index == df.index[i]] for i in range(len(set(df.index)))]
    session_gcds = [session_gcd(x) for x in sessions]
    return np.mean(session_gcds)

def main():
    log_path = "./output/1.txt"
    # log = load_log(log_path)()
    
    print(log_gcd(load_log(log_path)()))

if __name__ == '__main__':
    main()

