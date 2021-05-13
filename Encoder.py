class Encoder:
    base64chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

    def base64encode(self, s):
        i = 0
        base64 = ending = ''

        pad = 3 - (len(s) % 3)
        if pad != 3:
            s += "A" * pad
            ending += '=' * pad

        while i < len(s):
            b = 0

            for j in range(0, 3, 1):
                n = ord(s[i])
                i += 1

                b += n << 8 * (2 - j)

            base64 += self.base64chars[(b >> 18) & 63]
            base64 += self.base64chars[(b >> 12) & 63]
            base64 += self.base64chars[(b >> 6) & 63]
            base64 += self.base64chars[b & 63]

        if pad != 3:
            base64 = base64[:-pad]
            base64 += ending

        return base64

    def base64decode(self, s):
        i = 0
        base64 = decoded = ''
        if s[-2:] == '==':
            s = s[0:-2] + "AA"
            padding = 2
        elif s[-1:] == '=':
            s = s[0:-1] + "A"
            padding = 1
        else:
            padding = 0
        while i < len(s):
            d = 0
            for j in range(0, 4, 1):
                d += self.base64chars.index(s[i]) << (18 - j * 6)
                i += 1

            decoded += chr((d >> 16) & 255)
            decoded += chr((d >> 8) & 255)
            decoded += chr(d & 255)

        decoded = decoded[0:len(decoded) - padding]

        return decoded


a = Encoder()
text = a.base64encode("11fbfe3185374b8b99aa624c38ceaef7")
print(text)
text = a.base64decode(text)
print(text)
