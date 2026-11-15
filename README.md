> [!IMPORTANT]
> **1. I will not be actively checking if Wuolah's devs have patched this method. Whenever it gets, just open an issue to notify me, and in case that I am not too busy or feel needy, I will try to update it.**
>
> 2. Other thing, in case that you are planning to **~steal~** *use as inspiration* this repo (idc if it's for a LinkedIn publication or because you want to feel as "an university hero"), it's okay, but at least add me to the credits, don't be greedy ^^.
>
> 3. If you are part of **Wuolah team** no matter of you business role, don't take this repo as an **Attack**. Take it as a way to keep improving your security. Anyways, if you want to keep this repo hidden for whatever reason, you don't need to take it down, just dm at **LinkedIn** and we can talk directly.

# What's this
A smart way to download any **Wuolah PDF** as if you were a PRO user, **without** watching to any ad nor **losing your time** at wait lines.

# The reason behind this research
Maybe this could feel a bit disheartening for someone, but this development is not promoted by any philosophical reason in specific, it's just the result of a curious engineer + procastination in it's pure meaning.

It's true that nowadays Wuolah it's flooded with ads, for that reason there are plenty serious projects, such as, [GulagCleaner](https://github.com/YM162/gulagcleaner), or [WuolahExtra](https://github.com/pablouser1/WuolahExtra). My kudos on them, keep the good work.


# How to use it
This user guide is expected to be as clear as possible, to be understood even for those who even don't know what a "Hello World" is.

1. First, you have to clone this repo. Supposing you have already installed git and Python, just execute:
```bash
git clone https://github.com/mgp214UAL/XorLah.git 
```
2. Nav to XorLah directory:
```bash
cd XorLah
```
3. Install the requests python module:
```bash
pip install -r requirements.txt
```
4. Execute the script:
```bash
py main.py
```
5. The file is going to ask you for two parameters:
    * **URL**: You must to introduce the preview file URL, e.g: https://wuolah.com/apuntes/estructura-de-computadores-2/parcial-2-hecho-clase-pdf-14445576
    * **PDF Name**: The name of the output PDF, e.g: parcial_2_hecho_clase
6. If everything has succeeded, in the same directory, you will find the expected PDF without ads :P

# How
If this can be called as this, the "exploit" merely consists, in reversing their PDF "encryption" technique. I guess they have implemented this functionality to avoid leechers trying to download PDFs directly from the preview. This "vulnerability" appears because:
1. XOR is reversible by itself as it's symmetrical ((x ^ k) ^ k = x), so it **should not be used as an encryption technique**.
2. Every encryption || decryption attempt that occurs on the nav. side, it's practically a vulnerability. No matter how much effort you invest in hiding it, it can be reversed as it's directly exposed to the attacker.

This is their actual implementation (at 15.11.26):
```javascript
function i(e, r) {
            let n = t();
            return (i = function(e, r) {
                return n[e -= 345]
            }
            )(e, r)
        }

function o(e) {
            let r = i
              , n = new Uint8Array(e)
              , t = Math[r(345)](128, n[r(355)]);
            for (let e = 0; e < t; e++)
                n[e] ^= 27;
            return n
        }
```
Combining these facts with:
1. The URI of a file can be fully reconstructed as it's identifier is a visual 8 digits value (appended at the last hyphen of the preview, e.g: 12345678)
2. There is no need to be authenticated to access to the encrypted PDF.
= Downloads without ads nor accounts at Wuolah ;)

That's all for now, mates :3

**~ ssnov**