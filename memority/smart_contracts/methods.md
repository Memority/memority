# Contract methods v0.1
## Memority Token

**buy()**  
купить токены. можно просто сделать перевод на адрес контракта.       

**sell(uint256 amount)**  
продать (amount) токенов.  

**mintToken(uint256 mintedAmount)**  
создать новые токены. 
только владелец контракта.  

**setPrices(uint256 _tokenPrice)**  
установить цену ETH за 1 токен MMR. цена в wei.  
только владелец контракта.  

**setReward(uint256 _reward)**  
установить награду в wei токенах (_reward) ха хранение одного байта в течении часа.  
только владелец контракта.  

**setHoldersMinBalance(uint256 _tokens_wei)**  
установить минимальный необходимый размер баланса токенов в wei для начисления бонуса держателям.  
только владелец контракта.  

**doHoldersReward()**  
начислить токены держателям  

**balanceOf(address _owner)**  
баланс токенов пользователя (_owner). 

**withdrawAll()**  
перевести весь собранный эфир на адрес владельца контракта.   
только владелец контракта.  

**freezeAccount(address target, bool freeze)**   
заморозить/разморозить аккаунт (address).  
только владелец контракта.  

**freezePayouts(bool freeze)**   
заморозить/разморозить выплаты хостам.  
только владелец контракта.   

**buyAndDeposit(bytes32 _hash)**   
купить токены на сумму transact={'value': w3.toWei(1, 'ether')} и положить их на депозит файла (_hash).   

**deposits(address _address, bytes32 _hash)**   
получить размер депозита для файла (_hash) клиента (_address).  

**payouts(bytes32 _hash, address _address)**   
timestamp последней выплаты по файлу (_hash) хосту (_address).   

**timeToPay(bytes32 _hash)**  
return bool   
проверить прошел ли минимальный интервал для следующей выплаты по файлу (_hash).    

**hasDeposit(address _address, bytes32 _hash)**   
REMOVED. USE deposits(..., ...)

**requestPayout(address _address, bytes32 _hash)**   
return token amount    
инициализировать выплату хосту по файлу (_hash) владельца с контрактом (_address).        

**tokensPerByteHour()**  
цена за байт/час в wei токенах   

## Client contract
**makeDeposit(uint256 _value, bytes32 _hash)**  
Сделать депозит в токенах (_value) для оплаты периода хостинга для файла (_hash).    

**newFile(bytes32 hash, bytes32 name, uint size, address developer, address[] hosts)**   
добавить новый файл (hash) с именем (name), размером (size), разработчик приложения (developer).  
со списком хостов (hosts) на которые он уже загружен клиентом.        

**addHostToFile(bytes32 _hash)**   
новый хост для существующего файла (_hash).   
файлу должно нехватать копий.  
новый хост не может быть из оффлайн списка.

**replaceHost(bytes32 hash, address oldHost)**   
заменить хост (oldHost) для файла (hash).   
за замену хоста должно уже проголосовать больше половины активных хостов этого файла.    
  
**getFiles()**   
получить список хешей своих своих файлов.   

**getFileName(bytes32 _hash)**  
имя файла по хешу (_hash).  

**getFileSize(bytes32 _hash)**  
размер файла по хешу (_hash).  

**getFileDeveloper(bytes32 _hash)**  
адрес разработчика приложения по хешу (_hash) файла.  

**getFileHosts(bytes32 _hash)**     
список хостов файла (_hash).      

**voteOffline(address _address, bytes32 _hash)**   
проголосовать за исключение адреса (_address) из списка хостов файла (_hash).  
_address должен быть в списке хостов файла.  
голосующий должен быть в списке хостов файла.  
каждый хост может проголосовать только один раз за определенный хост.

**getOfflineVoters(bytes32 _hash, address _address)**   
получить список проголосовавших хостов за исключение хоста (_address) из хостов файла (_hash).   

**needCopy(bytes32 _hash)**   
для файла (_hash) надо добавить копию.   

**needReplace(address _address, bytes32 _hash)**   
хост (_address) для файла (_hash) ждет замены по причине недоступности. 

## MemoDB  
**transactionsCount(address _address)**  
Кол-во транзакций для адреса   

**transactionsId(address _address, i)**  
Получить уникальный хеш транзакции под номером i   

**transactions(_hash)**   
Детали транзакции    

**updateHost(bytes32 ip)**  
добавить/обновить хост. 
если хост уже есть в списке произойдет смена его ip.   

**getHosts()**  
returns address[]   
получить список хостов.  

**getHostIp(address hostAddress)**  
returns IP  
получить IP по адресу хоста.   
 
**clientContract(address _address)**  
return address  
получить адрес клиентского контракта по его личному адресу    

 
# Work logic  
## Hoster 
*1.* создаем новый хост указав свой ip. также вызываем эту функции при смени ip. 
```
token_contract.updateHost('50.50.250.30')
```
*2.* принимаем и сохраняем файл клиента напрямую от клиента вместе со списком других хостов для этого файла. также получаем от клиента адрес его контракта (для дальнейшего взаимодействия с ним).    
*3.* каждый хост получает свое время в минутах каждого часа в которое он будет проводить мониторинг.   
*4.* проверка всех хостов для каждого файла в назначенное время.   
*4.1* проверяем есть ли необходимость создать копию (без замены какого либо хоста). после копирования принявший (новый) хост сообщает в контракт клиента о себе.    
```
monitor_host:   
client_contract.needCopy('file_hash')  

new_host:  
client_contract.addHostToFile('file_hash') 
``` 

*4.2.* в случаи недоступности файла обновляем локальную статистику доступности. если файл недоступен на определенном хосте больше 3 часов голосуем через клиентский контракт. после проверяем необходимость замены хоста и в случаи положительного ответа выбираем из своего списка приоритетный новый хост и отдаем ему копию файла. новый хост по завершению сообщает в контракт клиента о себе и адрес хоста который он заменил.     
```
monitor_host:   
client_contract.voteOffline('0x24143873e0e0__offline_address__', 'file_hash')  
client_contract.needReplace('0x24143873e0e0__offline_address__', 'file_hash')  

new_host:  
client_contract.replaceHost('file_hash', '0x2414387__address_to_replce__') 
```  
*5.* в настройках хоста задается частота запроса выплат (по умолчанию раз в 14 дней). сначала через контракт Токенов проверяем доступность выплат по времени и есть ли баланс на счету клиента. если баланс нулевой удаляем файл (отправляем копию на почту?) в противном случае запрашиваем выплату.   
```
token_contract.timeToPay('file_hash')   
token_contract.hasDeposit('0x24143873e0f__client_contract_address__', 'file_hash')   
token_contract.requestPayout('0x24143873e0f__client_contract_address__', 'file_hash')   
``` 

## Client   
*1.* Запускаем свой контракт, получаем его адрес.   
```
w3.personal.unlockAccount(w3.eth.accounts[0], 'PASSWORD')   
contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])    
tx_hash = contract.deploy(transaction={'from': w3.eth.accounts[0], 'gas': gas}, args=['0x6569__token_comtract_address'])   
... w3.eth.getTransactionReceipt(tx_hash)   

```
*2.* считаем хеш файла, покупаем токены и делаем депозит для этого файла.   
```
//
file_hash = md5(оригинальный файл + соль)

// unlock account and buy for 1 ETH   
w3.personal.unlockAccount(w3.eth.accounts[0], 'PASSWORD')   
w3.eth.sendTransaction({
        'to': token_address,
        'from': w3.eth.accounts[0],
        'value': w3.toWei(1, 'ether'),
        'gas': 200000
    })

client_contract.makeDeposit(10000, file_hash)        
```   
*3.* получаем список хостов   
```
token_contract.getHosts()  
```
*4.* загружаем файл на 10 (берем из настроек) хостов сообщив им адрес своего контракта и заносим запись в свой контракт.   
```
client_contract.newFile(hash, name, size, address[])
```  
*5.* при запуски программы обновляем информацию по депозиту (сколько времени осталось) с возможностью повторить его.   
*6.* для загрузки файла получаем список хешей файлов по ним для каждого получаем имя и список хостов с которых скачиваем.  
```
client_contract.getFiles()   
client_contract.getFileName(hash)  
client_contract.getFileHosts(hash)   
```