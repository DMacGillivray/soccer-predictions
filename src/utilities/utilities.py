import pandas as pd
from pathlib import Path


# https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python


class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


def get_feature_names(df):
    features = sorted(list(set([col.split('-')[0] for col in
                      df.columns if '-' in col])))
    return features


def get_all_feature_cols(df):
    all_feature_cols = [col for col in df.columns if '-' in col]
    return all_feature_cols


def get_non_feature_cols(df):
    non_feature_cols = [col for col in df.columns if '-' not in col]
    return non_feature_cols


def get_ordinal_result_as_col(df):
    y = df['ordinal_result']
    return y


def make_stacked_season_readable(df_orig):
    """
    Note - This does not return ALL columns!
    """
    df = df_orig.copy(deep=True)
    first_cols = ['nation', 'league', 'season', 'h', 'a', 'date',
                  'h_ftGoals', 'a_ftGoals', 'result']
    h_feature_cols = sorted([col for col in df.columns if col[0:2] == 'h_'])
    a_feature_cols = sorted([col for col in df.columns if col[0:2] == 'a_'])
    full_odds_cols = sorted([col for col in df.columns if 'Odds' in col
                            and len(df[col].dropna()) == len(df)])

    df.sort_values(by=['season', 'date'], ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df_h = df[h_feature_cols].apply(pd.to_numeric,
                                    errors='coerce',
                                    downcast='float')
    df_a = df[a_feature_cols].apply(pd.to_numeric,
                                    errors='coerce',
                                    downcast='float')

    df_readable = pd.concat([df[first_cols], df_h, df_a, df[full_odds_cols]],
                            sort=False, axis=1)
    dropper_cols = [col for col in df_readable.columns if '2.5Odds' in col or
                    'asian' in col]
    df_readable.drop(columns=dropper_cols, inplace=True)
    list1 = ['hwinOddsBet365', 'drawOddsBet365', 'awinOddsBet365']
    if set(list1) <= set(df_readable.columns):
        mapping_dict = {col: col[0:8] for col in list1}
        df_readable.rename(columns=mapping_dict, inplace=True)

    return df_readable
