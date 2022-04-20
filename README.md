# fx-robot

### 基本的な流れ

1. Sell or Buyの仮説をたてる
2. 期待価格を設定
3. 実績データをもとにモデルの作成
4. 期待価格を入力し予測シミュレーション
5. Sell or Buy、期待価格を検証・評価して注文

See: [https://www.mql5.com/ja/docs/integration/python_metatrader5](https://www.mql5.com/ja/docs/integration/python_metatrader5)

### 必要なもの

- OANDA MT5のアカウント
- OANDA Meta Trader 5
- OSはWindows10, Python(3.9.12にて開発検証)
- 取引資金

### セットアップと実行

```
python -m virtualenv vmql5

source vmql5/Scripts/activate

git clone git@github.com:tasat31/fx-robot.git

cd fx-robot

pip install -r requirements.txt

cp robots/.env.sample robots/.env

* .envにMT5接続情報を設定する

# 実行
python main.py
```

### 問題があった場合

[https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes](https://www.mql5.com/en/docs/constants/errorswarnings/enum_trade_return_codes)


### よくあるエラー

- order_send failed, retcode=10027　-> MT5Traderで「アルゴリズム取引」を有効にする
- order_send failed, retcode=10030　-> 証拠金不足

### 開発手順

formatter --- black

linter --- flake8
