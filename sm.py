NO_OF_CHARS = 256


def badCharHeuristic(string, size):
    badChar = [-1]*NO_OF_CHARS
    for i in range(size):
        badChar[ord(string[i])] = i
    return badChar


def search(txt, pat):
    m = len(pat)
    n = len(txt)
    badChar = badCharHeuristic(pat, m)
    s = 0
    ans = []
    while(s <= n-m):
        j = m-1
        while j >= 0 and pat[j] == txt[s+j]:
            j -= 1
        if j < 0:
            ans.append(s)
            s += (m-badChar[ord(txt[s+m])] if s+m < n else 1)
        else:
            s += max(1, j-badChar[ord(txt[s+j])])
    return ans

def get_Score(pat, obj):
    ans = {}
    Max = 0;
    for i in obj:
        foo = search(i['name'], pat)
        Max = max(len(foo), Max)
        try:
            ans[len(foo)].append(i)
        except :
            ans[len(foo)] = []
            ans[len(foo)].append(i)
    ret = []
    print(ans)
    for i in range(0,Max+1):
        try:
            for j in ans[i]:
                ret.append(j)
        except:
            pass
    return ret


def main():
    txt = "PPPUPUPU"
    pat = "PU"
    obj = [
        {
            "_id": "6074560748a87c736b5eedf0",
            "email": "s@gmail.com",
            "name": "PPPUPUPU"
        },
        {
            "_id": "6074560748a87c736b5eedf0",
            "email": "s@gmail.com",
            "name": "s"
        }
    ]
    ans = get_Score(pat, obj)
    # print(ans)


if __name__ == '__main__':
    main()