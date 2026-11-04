# FixturePress

Bir hata imzasını koruyarak JSON alanlarını ve liste elemanlarını azaltır.

## Kullanım

Python 3.11 veya üzeri.

```sh
python fixturepress.py input.json -o small.json -- python repro.py '{}'
```

{} geçici aday dosyasının yoluyla değiştirilir. Varsayılan imza çıkış kodu ve son dolu çıktı satırıdır. --match alternatif regex, --runs çalışma sınırıdır. Her deneme verilen komutu gerçekten çalıştırır.

## Doğrulama

```sh
python verify.py
```

MIT lisansı.
