import numpy as np

# epoching

def ft_stim(cond='all'):
    conds = {'memory': {
            'condition':'memory',
            'trial': {
                'begin':'Stim/S  5',
                'end':'Stim/S  6'
            },
            'stimulus': {
                'begin':'Stim/S 10',
                'end':'Stim/S 11'
            },
            'probe': {
                'begin':'Stim/S 12',
                'end':'Stim/S 13'
            },
            'block': {
                'memory': {
                    'begin':'Stim/S  3',
                    'end':'Stim/S  4'
            }},
            'response': {
                'begin': 'Stim/30',
                'types': {
                    'main': { 'correct':'Stim/S 34','incorrect':'Stim/S 35' },
                    'aux': { 'different':'Stim/S 31', 'identical':'Stim/S 32'}
                }},
            'feedback': {
                'begin': 'Stim/S 40',
                'end': 'Stim/S 41'
            },
            'reaction': {
                'begin':['Stim/S 12'],
                'end':['Stim/S 30']
            },
            'require': ['Stim/S 10']
    },
    'control': {
            'condition':'control',
            'trial': {
                'begin':'Stim/S 15',
                'end':'Stim/S 16'
            },
            'stimulus': {
                'begin':'Stim/S 17',
                'end':'Stim/S 18'
            },
            'probe': {
                'begin':'Stim/S 20',
                'end':'Stim/S 21'
            },
            'block': {
                'control': {
                    'begin':'Stim/S  7',
                    'end':'Stim/S  8'
            }},
            'response': {
                'begin': 'Stim/30',
                'types': {
                    'main': { 'correct':'Stim/S 38','incorrect':'Stim/S 39' },
                    'aux': { 'left':'Stim/S 36', 'right':'Stim/S 37'}
                }},
            'feedback': {
                'begin': 'Stim/S 50',
                'end': 'Stim/S 51'
            },
            'reaction': {
                'begin':['Stim/S 20'],
                'end':['Stim/S 30']
            },
            'require': ['Stim/S 17']
    }}
    return conds.get(cond,list(conds.values()))

def multimodal(cond="all"):
    conds = {'visual': {
            'condition':'visual',
            'trial': {
                'begin':'Stim/S  9',
                'end':'Stim/S 10'
            },
            'stimulus': {
                'begin':'Stim/S 14',
                'end':'Stim/S 15',
                'types': {
                    'main': {
                        '0':'Stim/S 20',
                        '45':'Stim/S 21',
                        '90':'Stim/S 22',
                        '135':'Stim/S 23'
                }}},
            'block': {
                'visual/right': {
                    'begin':'Stim/S102',
                    'end':'Stim/S104'
                },
                'visual/left': {
                    'begin':'Stim/S108',
                    'end':'Stim/S110'
            }},
            'response': {
                'types': {
                    'main': {
                        'R/left':'Stim/S 60','R/down':'Stim/S 61','R/right':'Stim/S 62','R/up':'Stim/S 63',
                        'L/left':'Stim/S 64','L/down':'Stim/S 65','L/right':'Stim/S 66','L/up':'Stim/S 67'
            }}},
            'feedback': {
                'types': {
                    'main': {
                        'positive': 'Stim/S 50','negative':'Stim/S 52','neutral':'Stim/S 54'
            }}},
            'reaction': {
                'begin':['Stim/S 14'],
                'end':['Stim/S 60','Stim/S 61','Stim/S 62','Stim/S 63','Stim/S 64','Stim/S 65','Stim/S 66','Stim/S 67']
            },
            'require': ['Stim/S 20','Stim/S 21','Stim/S 22','Stim/S 23']
    },
    'auditive': {
            'condition':'auditive',
            'block': {
                'auditive/left': {
                    'begin':'Stim/S105',
                    'end':'Stim/S107'
                },
                'auditive/right': {
                    'begin':'Stim/S111',
                    'end':'Stim/S113'
            }},
            'trial': {
                'begin':'Stim/S  9',
                'end':'Stim/S 10'
            },
            'stimulus': {
                'begin':'Stim/S 14',
                'end':'Stim/S 15',
                'types': {
                    'main':{
                        '250':'Stim/S 16',
                        '500':'Stim/S 17',
                        '1000':'Stim/S 18',
                        '2000':'Stim/S 19'
            }}},
            'response': {
                'types': {
                    'main': {
                        'R/left':'Stim/S 60','R/down':'Stim/S 61','R/right':'Stim/S 62','R/up':'Stim/S 63',
                        'L/left':'Stim/S 64','L/down':'Stim/S 65','L/right':'Stim/S 66','L/up':'Stim/S 67'
            }}},
            'feedback': {
                'types': {
                    'main': {
                        'positive': 'Stim/S 50','negative':'Stim/S 52','neutral':'Stim/S 54'
            }}},
            'reaction': {
                'begin':['Stim/S 14'],
                'end':['Stim/S 60','Stim/S 61','Stim/S 62','Stim/S 63','Stim/S 64','Stim/S 65','Stim/S 66','Stim/S 67']
            },
            'require': ['Stim/S 16','Stim/S 17','Stim/S 18','Stim/S 19']
    }}
    return conds.get(cond,conds)

def probabilistic(cond="all"):
    conds = {'train': {
            'condition': 'train',
            'block': { # DONE
                'train': {
                    'begin':'Stim/100',
                    'end':'Stim/101'
            }},
            'trial': { # DONE
                'begin':'Stim/5',
                'end':'Stim/6'
            },
            'stimulus': { # DONE
                'begin':'Stim/12',
                'end':'Stim/13',
                'types': {
                    'main': {'AB':'Stim/14','CD':'Stim/15','EF':'Stim/16'},
                    'aux':{'ltr':'Stim/41','rtl':'Stim/42','correct':'Stim/51','incorrect':'Stim/52'}
            }},
            'response': {
                'begin': 'Stim/30',
                'types': {
                    'main':{'correct':'Stim/34','incorrect':'Stim/31'},
                    'aux': {'left':'Stim/37','right':'Stim/38'}
            }},
            'feedback': {
                'begin': 'Stim/20',
                'types': {
                    'main':{'positive': 'Stim/22','negative':'Stim/23','neutral':'Stim/24'}
            }},
            'reaction': {
                'begin':['Stim/12'],
                'end':['Stim/30']
            },
            'require': ['Stim/14','Stim/15','Stim/16']
    },
    'test': {
        'condition': 'test',
            'block': {
                'test': {
                    'begin':'Stim/102',
                    'end':'Stim/103'
            }},
            'trial': {
                'begin':'Stim/17',
                'end':'Stim/18'
            },
            'stimulus': {
                'begin':'Stim/12',
                'end':'Stim/13',
                'types': {
                    'main': {'GG':'Stim/81','NG':'Stim/82','NN':'Stim/83'},
                    'aux': {'A':'Stim/71','B':'Stim/72','C':'Stim/73','D':'Stim/74','E':'Stim/75','F':'Stim/76'}
            }},
            'response': {
                'begin': 'Stim/30',
                'types': {
                    'main': {'correct': 'Stim/91','incorrect':'Stim/90'},
                    'aux': {'left':'Stim/37','right':'Stim/38'}
            }},
            'feedback': {
                'types': {
                    'main': {'positive': 'Stim/91','negative':'Stim/90'}
            }},
            'reaction': {
                'begin':['Stim/12'],
                'end':['Stim/30']
            },
            'require': ['Stim/81','Stim/82','Stim/83']
    }}
    return conds.get(cond,conds)

def dmss(cond="all"):
    conds = {'dmss': {
            'condition':'dmss',
            'block': {
                'dmss': {
                    'begin':'Stim/S  3',
                    'end':'Stim/S  4'
                }},
            'trial': {
                'begin':'Stim/S  5',
                'end':'Stim/S  6'
            },
            'delay': {
                'begin': 'Stim/S 50',
                'end': 'Stim/ 51',
                'types': {
                    'main':{
                        'delay': 'Stim/S 50'
            }}},
            'probe': {
                'begin':'Stim/S 57',
                'end':'Stim/S 58',
                'types': {
                    'main':{
                        'probe':'Stim/S 57'
                    },'aux': {
                        'size1':'Stim/S 72','size2':'Stim/S 73','size4':'Stim/S 74'
                    }}},
            'stimulus': {
                'begin':'Stim/S 57',
                'end':'Stim/S 58',
                'types': {
                    'main':{
                        'size1':'Stim/S 11','size2':'Stim/S 21','size4':'Stim/S 31'
                    },'aux': {
                        'psize1':'Stim/S 72','psize2':'Stim/S 73','psize4':'Stim/S 74'
                    }}},
            'response': {
                'types': {
                    'main': {
                        'left':'Stim/S 61','right':'Stim/S 62'
                    },'aux':{
                        'correct':'Stim/S 64','incorrect':'Stim/S 65'
                }}},
            'feedback': {
                'types': {
                    'main': {
                        'size1': 'Stim/S 72','size2':'Stim/S 73','size4':'Stim/S 74'
                    },'aux': {
                        'positive': 'Stim/S 64','negative':'Stim/S 65'
                    }
                }},
            'reaction': {
                'begin':['Stim/S 57'],
                'end':['Stim/S 60']
            },
            'require': ['Stim/S 57']
    }}
    return conds.get(cond,conds)

# modelling

factor_fn = {'Modality': lambda x: (x['Modality']=='visual')*1-(x['Modality']=='auditive')*1,
             'Visual': lambda x: (x['Modality']=='visual')*1,
             'Auditory': lambda x: (x['Modality']=='auditive')*1,
             'FeedbackType': lambda x: (x['FeedbackType']=='positive')*1-(x['FeedbackType']=='negative')*1,
             'BlockTime': lambda x: (x['BlockPosition']=='Begin')*1-(x['BlockPosition']=='End')*1,
             'BlockTime': lambda x: (x['BlockPosition']=='Begin')*1-(x['BlockPosition']=='End')*1,
             'Intercept': lambda x: np.ones((len(x),))
            }

factor_tl = {'Modality': "Effect of modality (visual-auditory), {}-locked, subject {}",
             'Visual': "Effect of modality (visual), {}-locked, subject {}",
             'Auditory': "Effect of modality (auditory), {}-locked, subject {}",
             'FeedbackType': "Effect of response correctness (correct - incorrect), {}-locked, subject {}",
             'BlockTime': "Effect of trial position in block, {}-locked, subject {}",
             'Intercept': "Basal activity, {}-locked, subject {}"
            }
