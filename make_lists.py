#!/usr/bin/env python

from random import randint


def read_lines(file_path):
    with open(file_path, 'r') as f:
        line = f.readline().rstrip()
        while line:
            yield line
            line = f.readline().rstrip()


def random_iterator(max_val, degree=1):
    """
    Degree changes the distribution. 1 is uniform. 2 and above are normal
    distributions of various deviations. The method used is a little crude
    on small source arrays, but whatever.
    """
    max_ix = [int(max_val / degree) for r in range(1, degree)]
    max_ix.append(max_val - sum(max_ix))

    while True:
        yield randint(0, max_val - 1)


def random_item(source):
    max_ix = len(source) - 1

    while True:
        yield source[randint(0, max_ix)]


def make_people(people_cnt):
    firsts = list(read_lines('src_lists/first_names.txt'))
    lasts = list(read_lines('src_lists/last_names.txt'))

    with open('trg_lists/people.txt', 'w') as f:
        dupeset = set()
        ix = 0

        for fn, ln in zip(
            random_item(firsts),
            random_item(lasts)
        ):
            k = (fn, ln)
            if k in dupeset:
                continue
            dupeset.add(k)

            for x in [str(ix), ",", fn, " ", ln, "\n"]:
                f.write(x)
            ix += 1
            if ix == people_cnt:
                break


def make_companies(company_cnt):
    with open('trg_lists/companies.txt', 'w') as f:
        adjectives = list(read_lines('src_lists/adjectives.txt'))
        nouns = list(read_lines('src_lists/nouns.txt'))
        suffixes = list(read_lines('src_lists/suffixes.txt'))

        dupeset = set()
        ix = 0
        for a, n, s in zip(
            random_item(adjectives),
            random_item(nouns),
            random_item(suffixes)
        ):
            k = (a, n, s)
            if k in dupeset:
                continue
            dupeset.add(k)

            for x in [str(ix), ",", a, " ", n, " ", s, "\n"]:
                f.write(x)
            ix += 1
            if ix == company_cnt:
                break


def make_people_companies(people_cnt, company_cnt):
    # note that we are going up to degree 3 with companies, which should create
    # an uneven but normal distribution of employee counts
    def generate_rows():
        company_iter = random_iterator(company_cnt, 3)
        for p_id in range(people_cnt):
            id_1 = p_id * 2
            id_2 = id_1 + 1

            c_id1 = next(company_iter)
            c_id2 = c_id1
            while c_id1 == c_id2:
                c_id2 = next(company_iter)
            yield id_1, p_id, min(c_id1, c_id2)
            yield id_2, p_id, max(c_id1, c_id2)

    with open('trg_lists/people_companies_id.txt', 'w') as f1:
        with open('trg_lists/people_companies.txt', 'w') as f2:
            for id, p_id, c_id in generate_rows():
                f1.write(str(id))
                f1.write(",")

                for x in [str(p_id), ",", str(c_id), "\n"]:
                    for f in [f1, f2]:
                        f.write(x)


if __name__ == '__main__':
    people_cnt = 1000000
    company_cnt = 1000000

    # make_people(people_cnt)
    # print('Made people')

    # make_companies(company_cnt)
    # print('Made companies')

    make_people_companies(people_cnt, company_cnt)
    print('Made people_companies and people_companies_id')
