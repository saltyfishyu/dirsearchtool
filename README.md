# dirsearchtool

### A tool base on dirsearch

* Why?

  >[基于dirsearch的SRC工具](http://saltyfishyu.xmutsec.com/index.php/2019/09/07/51.html)

* How?

  >targets.txt(a lots of url)

  >`python3 dirsearch.py -L target.txt -e php --json-report=./reports/target/target-report.json`

  >in ./reports/target/ ( target-report.json & json-to-file.py)

  >`python json-to-file.py -i target-report.json`
  
  >in ./reports/target/ ( target-report.json & json-to-file.py & target-report.html & target-report-200.html)

* Update

  >v1.0 None

  >v1.1 thread & checkwaf
  