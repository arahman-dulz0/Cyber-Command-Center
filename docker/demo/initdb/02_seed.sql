-- =============================================================================
-- Cyber Command Center — demo dataset
--
-- Populates the demo stack so the dashboard is impressive out-of-the-box. Every
-- CVE below is REAL and publicly documented (NVD/CISA KEV) — nothing is
-- fabricated. Timestamps are relative to first boot so the "last 24h / 7 days"
-- panels light up. Runs once, on first Postgres init, after 01_schema.sql.
-- =============================================================================

-- --- CVEs (real, famous) -----------------------------------------------------
INSERT INTO cves (cve_id, title, description, cvss_score, severity, published_date, ai_summary, posted_to_discord, created_at) VALUES
('CVE-2021-44228','Apache Log4j2 JNDI RCE (Log4Shell)','Apache Log4j2 <=2.14.1 JNDI features used in configuration, log messages, and parameters do not protect against attacker-controlled LDAP and other JNDI related endpoints, allowing remote code execution.',10.0,'CRITICAL',NOW()-INTERVAL '3 hours','Log4Shell: trivially exploitable unauthenticated RCE in Apache Log4j; mass-exploited, patch or mitigate immediately.',TRUE,NOW()-INTERVAL '3 hours'),
('CVE-2021-45046','Apache Log4j2 Thread Context DoS/RCE','Incomplete fix for CVE-2021-44228 in Apache Log4j 2.15.0 allows attackers with control over Thread Context Map data to cause DoS and, in some configurations, remote code execution.',9.0,'CRITICAL',NOW()-INTERVAL '5 hours','Follow-up Log4j flaw; upgrade to 2.16+ as 2.15 fix was incomplete.',TRUE,NOW()-INTERVAL '5 hours'),
('CVE-2022-22965','Spring Framework RCE (Spring4Shell)','A Spring MVC or Spring WebFlux application running on JDK 9+ may be vulnerable to remote code execution via data binding when deployed as a WAR on Apache Tomcat.',9.8,'CRITICAL',NOW()-INTERVAL '7 hours','Spring4Shell: RCE in Spring on Tomcat via data binding; widely weaponised.',TRUE,NOW()-INTERVAL '7 hours'),
('CVE-2022-1388','F5 BIG-IP iControl REST Auth Bypass RCE','Undisclosed requests may bypass iControl REST authentication in F5 BIG-IP, allowing an unauthenticated attacker to execute arbitrary system commands.',9.8,'CRITICAL',NOW()-INTERVAL '9 hours','F5 BIG-IP auth-bypass to root command execution; internet-facing devices at high risk.',TRUE,NOW()-INTERVAL '9 hours'),
('CVE-2023-34362','Progress MOVEit Transfer SQL Injection RCE','A SQL injection vulnerability in Progress MOVEit Transfer allows an unauthenticated attacker to access the database and execute code; exploited en masse by the Cl0p ransomware group.',9.8,'CRITICAL',NOW()-INTERVAL '11 hours','MOVEit zero-day driving the Cl0p mass-extortion campaign; assume compromise if unpatched.',TRUE,NOW()-INTERVAL '11 hours'),
('CVE-2023-4966','Citrix NetScaler ADC/Gateway Info Disclosure (Citrix Bleed)','Sensitive information disclosure in Citrix NetScaler ADC and NetScaler Gateway allows session-token theft and MFA bypass when configured as a gateway or AAA virtual server.',9.4,'CRITICAL',NOW()-INTERVAL '14 hours','Citrix Bleed: leaks session tokens enabling MFA bypass; actively exploited by ransomware affiliates.',TRUE,NOW()-INTERVAL '14 hours'),
('CVE-2024-3400','Palo Alto PAN-OS GlobalProtect Command Injection','A command injection in the GlobalProtect feature of Palo Alto Networks PAN-OS allows an unauthenticated attacker to execute arbitrary code with root privileges on the firewall.',10.0,'CRITICAL',NOW()-INTERVAL '17 hours','PAN-OS GlobalProtect unauth root RCE; exploited as a zero-day, patch urgently.',TRUE,NOW()-INTERVAL '17 hours'),
('CVE-2024-1709','ConnectWise ScreenConnect Auth Bypass','An authentication bypass using an alternate path in ConnectWise ScreenConnect allows attackers to create administrator accounts and take over the server.',10.0,'CRITICAL',NOW()-INTERVAL '20 hours','ScreenConnect trivial auth bypass; mass-exploited within days of disclosure.',TRUE,NOW()-INTERVAL '20 hours'),
('CVE-2023-20198','Cisco IOS XE Web UI Privilege Escalation','A vulnerability in the web UI of Cisco IOS XE allows an unauthenticated remote attacker to create a privileged account and gain full control of the device.',10.0,'CRITICAL',NOW()-INTERVAL '22 hours','Cisco IOS XE zero-day used to implant thousands of devices; disable the web UI.',TRUE,NOW()-INTERVAL '22 hours'),
('CVE-2024-23897','Jenkins CLI Arbitrary File Read','Jenkins allows unauthenticated attackers to read arbitrary files via the built-in command line interface args4j parser, which can lead to full remote code execution.',9.8,'CRITICAL',NOW()-INTERVAL '26 hours','Jenkins arbitrary file read escalating to RCE; patch and restrict CLI access.',TRUE,NOW()-INTERVAL '26 hours'),
('CVE-2023-22515','Atlassian Confluence Broken Access Control','Broken access control in Confluence Data Center and Server allows unauthenticated attackers to create administrator accounts and access instances.',10.0,'CRITICAL',NOW()-INTERVAL '30 hours','Confluence privilege escalation exploited in the wild; create-admin primitive.',TRUE,NOW()-INTERVAL '30 hours'),
('CVE-2022-26134','Atlassian Confluence OGNL Injection RCE','An unauthenticated OGNL injection vulnerability in Confluence Server and Data Center allows remote code execution.',9.8,'CRITICAL',NOW()-INTERVAL '34 hours','Confluence OGNL zero-day; unauthenticated RCE, patched June 2022.',TRUE,NOW()-INTERVAL '34 hours'),
('CVE-2021-26855','Microsoft Exchange SSRF (ProxyLogon)','A server-side request forgery in Microsoft Exchange Server allows an attacker to send arbitrary HTTP requests and authenticate as the Exchange server, part of the ProxyLogon chain.',9.8,'CRITICAL',NOW()-INTERVAL '38 hours','ProxyLogon SSRF chained to RCE on Exchange; mass-exploited by HAFNIUM.',TRUE,NOW()-INTERVAL '38 hours'),
('CVE-2022-41040','Microsoft Exchange SSRF (ProxyNotShell)','A server-side request forgery in Microsoft Exchange allows an authenticated attacker to elevate privileges, chained with CVE-2022-41082 for RCE.',8.8,'HIGH',NOW()-INTERVAL '42 hours','ProxyNotShell SSRF half of the Exchange RCE chain.',TRUE,NOW()-INTERVAL '42 hours'),
('CVE-2022-41082','Microsoft Exchange RCE (ProxyNotShell)','A remote code execution vulnerability in Microsoft Exchange PowerShell backend, chained with CVE-2022-41040.',8.8,'HIGH',NOW()-INTERVAL '46 hours','ProxyNotShell RCE half; authenticated code execution on Exchange.',TRUE,NOW()-INTERVAL '46 hours'),
('CVE-2020-1472','Netlogon Elevation of Privilege (Zerologon)','An elevation of privilege in the Netlogon Remote Protocol (MS-NRPC) allows an attacker to establish a vulnerable Netlogon session and become domain administrator.',10.0,'CRITICAL',NOW()-INTERVAL '50 hours','Zerologon: instant domain-admin takeover; a top ransomware enabler.',TRUE,NOW()-INTERVAL '50 hours'),
('CVE-2021-34527','Windows Print Spooler RCE (PrintNightmare)','A remote code execution vulnerability in the Windows Print Spooler service allows attackers to run arbitrary code with SYSTEM privileges.',8.8,'HIGH',NOW()-INTERVAL '54 hours','PrintNightmare SYSTEM RCE via Print Spooler; disable spooler where possible.',TRUE,NOW()-INTERVAL '54 hours'),
('CVE-2022-30190','Microsoft MSDT RCE (Follina)','A remote code execution vulnerability in the Microsoft Support Diagnostic Tool (MSDT) when called from Office documents.',7.8,'HIGH',NOW()-INTERVAL '58 hours','Follina: Office-to-MSDT RCE requiring no macros.',TRUE,NOW()-INTERVAL '58 hours'),
('CVE-2023-27997','Fortinet FortiOS SSL-VPN Heap Overflow (XORtigate)','A heap-based buffer overflow in FortiOS and FortiProxy SSL-VPN allows a remote attacker to execute arbitrary code or commands via crafted requests.',9.8,'CRITICAL',NOW()-INTERVAL '62 hours','FortiOS SSL-VPN pre-auth RCE; internet-facing Fortinet devices at risk.',TRUE,NOW()-INTERVAL '62 hours'),
('CVE-2022-42475','Fortinet FortiOS SSL-VPN Heap Overflow','A heap-based buffer overflow in FortiOS SSL-VPN allows a remote unauthenticated attacker to execute arbitrary code, exploited as a zero-day.',9.8,'CRITICAL',NOW()-INTERVAL '66 hours','FortiOS heap overflow exploited in the wild against government targets.',TRUE,NOW()-INTERVAL '66 hours'),
('CVE-2024-21887','Ivanti Connect Secure Command Injection','A command injection in Ivanti Connect Secure and Policy Secure allows an authenticated administrator to execute arbitrary commands, chained with CVE-2023-46805.',9.1,'CRITICAL',NOW()-INTERVAL '70 hours','Ivanti command injection chained with auth bypass for unauth RCE.',TRUE,NOW()-INTERVAL '70 hours'),
('CVE-2023-46805','Ivanti Connect Secure Auth Bypass','An authentication bypass in the web component of Ivanti Connect Secure and Policy Secure allows a remote attacker to access restricted resources.',8.2,'HIGH',NOW()-INTERVAL '74 hours','Ivanti auth bypass; paired with CVE-2024-21887 for full compromise.',TRUE,NOW()-INTERVAL '74 hours'),
('CVE-2024-27198','JetBrains TeamCity Authentication Bypass','An authentication bypass in JetBrains TeamCity allows a remote unauthenticated attacker to take over the server and its build pipelines.',9.8,'CRITICAL',NOW()-INTERVAL '78 hours','TeamCity auth bypass enabling CI/CD supply-chain compromise.',TRUE,NOW()-INTERVAL '78 hours'),
('CVE-2023-3519','Citrix NetScaler ADC/Gateway RCE','An unauthenticated remote code execution in Citrix NetScaler ADC and Gateway, exploited as a zero-day to drop webshells.',9.8,'CRITICAL',NOW()-INTERVAL '82 hours','Citrix ADC zero-day RCE used to implant webshells on critical infrastructure.',TRUE,NOW()-INTERVAL '82 hours'),
('CVE-2021-21972','VMware vCenter Server vSphere Client RCE','An unauthenticated remote code execution in the vSphere Client (HTML5) due to a plugin that lacks authorization, affecting VMware vCenter Server.',9.8,'CRITICAL',NOW()-INTERVAL '88 hours','VMware vCenter unauth RCE via vSphere Client plugin; patch and restrict access.',TRUE,NOW()-INTERVAL '88 hours'),
('CVE-2019-0708','Microsoft RDP RCE (BlueKeep)','A remote code execution vulnerability in Remote Desktop Services (RDP) allows unauthenticated attackers to execute code, and is wormable.',9.8,'CRITICAL',NOW()-INTERVAL '96 hours','BlueKeep: wormable pre-auth RDP RCE reminiscent of WannaCry risk.',TRUE,NOW()-INTERVAL '96 hours'),
('CVE-2017-0144','Windows SMBv1 RCE (EternalBlue)','A remote code execution vulnerability in Microsoft SMBv1 exploited by the EternalBlue exploit and the WannaCry/NotPetya campaigns.',8.1,'HIGH',NOW()-INTERVAL '104 hours','EternalBlue SMBv1 RCE behind WannaCry/NotPetya; disable SMBv1.',TRUE,NOW()-INTERVAL '104 hours'),
('CVE-2024-6387','OpenSSH regreSSHion Signal Handler RCE','A signal handler race condition in OpenSSH server (sshd) allows unauthenticated remote code execution as root on glibc-based Linux systems.',8.1,'HIGH',NOW()-INTERVAL '110 hours','regreSSHion: unauth root RCE in OpenSSH; exploitation is difficult but real.',TRUE,NOW()-INTERVAL '110 hours'),
('CVE-2022-3602','OpenSSL X.509 Punycode Buffer Overflow','A stack buffer overflow in OpenSSL 3.0.x during X.509 certificate name constraint checking (punycode), initially rated critical.',7.5,'HIGH',NOW()-INTERVAL '118 hours','OpenSSL 3.0 punycode overflow; downgraded to high, patch to 3.0.7.',TRUE,NOW()-INTERVAL '118 hours'),
('CVE-2023-44487','HTTP/2 Rapid Reset DoS','A denial of service in the HTTP/2 protocol (rapid stream reset) enabling record-breaking DDoS attacks against web servers and proxies.',7.5,'HIGH',NOW()-INTERVAL '126 hours','HTTP/2 Rapid Reset driving hyper-volumetric DDoS; patch web tier.',TRUE,NOW()-INTERVAL '126 hours'),
('CVE-2024-3094','XZ Utils Backdoor (liblzma)','Malicious code introduced into XZ Utils liblzma (5.6.0/5.6.1) creates a backdoor in sshd on affected distributions via a supply-chain compromise.',10.0,'CRITICAL',NOW()-INTERVAL '134 hours','XZ Utils backdoor: a near-miss supply-chain compromise of sshd.',TRUE,NOW()-INTERVAL '134 hours'),
('CVE-2023-50164','Apache Struts Path Traversal RCE','A path traversal in Apache Struts file upload logic allows attackers to upload malicious files and achieve remote code execution.',9.8,'CRITICAL',NOW()-INTERVAL '140 hours','Apache Struts file-upload path traversal to RCE; patch immediately.',TRUE,NOW()-INTERVAL '140 hours'),
('CVE-2021-4034','Polkit pkexec Local Privilege Escalation (PwnKit)','A memory corruption in polkit''s pkexec allows any unprivileged local user to gain root privileges on default Linux installations.',7.8,'HIGH',NOW()-INTERVAL '150 hours','PwnKit: reliable local root on virtually all Linux distros.',TRUE,NOW()-INTERVAL '150 hours'),
('CVE-2022-0847','Linux Kernel Dirty Pipe Privilege Escalation','A flaw in the Linux kernel pipe handling (Dirty Pipe) allows a local user to overwrite read-only files and escalate to root.',7.8,'HIGH',NOW()-INTERVAL '158 hours','Dirty Pipe: overwrite read-only files for local root on Linux 5.8+.',TRUE,NOW()-INTERVAL '158 hours'),
('CVE-2023-38831','RARLabs WinRAR Spoofing RCE','A flaw in WinRAR allows execution of arbitrary code when a user opens a crafted archive, exploited by multiple APT groups.',7.8,'HIGH',NOW()-INTERVAL '164 hours','WinRAR archive spoofing used by APTs to run code on victim opening.',TRUE,NOW()-INTERVAL '164 hours'),
('CVE-2024-25600','WordPress Bricks Builder Unauthenticated RCE','An unauthenticated remote code execution in the Bricks theme/builder for WordPress allows attackers to execute arbitrary PHP.',9.8,'CRITICAL',NOW()-INTERVAL '15 hours','WordPress Bricks Builder unauth RCE actively exploited; update the theme.',TRUE,NOW()-INTERVAL '15 hours');

-- --- Enrichment (fusion: EPSS/KEV/exploit + CCC priority) ---------------------
INSERT INTO cve_enrichment (cve_id, epss, epss_percentile, kev, kev_ransomware, exploitdb_count, github_poc_count, patch_available, priority_score, priority_label, ai_risk, enriched_at) VALUES
('CVE-2021-44228',0.975,0.999,TRUE,TRUE,12,90,TRUE,100,'CRITICAL','Mass-exploited unauth RCE; assume active targeting. Patch to Log4j 2.17+ or remove JndiLookup.',NOW()-INTERVAL '3 hours'),
('CVE-2021-45046',0.72,0.97,TRUE,FALSE,4,25,TRUE,88,'CRITICAL','Bypass of the initial Log4Shell fix; upgrade to 2.16+.',NOW()-INTERVAL '5 hours'),
('CVE-2022-22965',0.955,0.999,TRUE,FALSE,8,60,TRUE,97,'CRITICAL','Weaponised Spring RCE on Tomcat; patch Spring and JDK config.',NOW()-INTERVAL '7 hours'),
('CVE-2022-1388',0.955,0.998,TRUE,FALSE,6,40,TRUE,96,'CRITICAL','F5 BIG-IP unauth command execution; restrict management interface.',NOW()-INTERVAL '9 hours'),
('CVE-2023-34362',0.94,0.998,TRUE,TRUE,3,20,TRUE,98,'CRITICAL','Cl0p ransomware mass-exploitation; hunt for webshells and data exfil.',NOW()-INTERVAL '11 hours'),
('CVE-2023-4966',0.94,0.998,TRUE,TRUE,4,35,TRUE,97,'CRITICAL','Citrix Bleed session hijack; patch and invalidate all active sessions.',NOW()-INTERVAL '14 hours'),
('CVE-2024-3400',0.94,0.998,TRUE,FALSE,3,18,TRUE,99,'CRITICAL','PAN-OS unauth root RCE exploited as zero-day; apply hotfix and check for implants.',NOW()-INTERVAL '17 hours'),
('CVE-2024-1709',0.96,0.999,TRUE,TRUE,5,45,TRUE,98,'CRITICAL','ScreenConnect trivial takeover; patch immediately, audit admin accounts.',NOW()-INTERVAL '20 hours'),
('CVE-2023-20198',0.90,0.997,TRUE,FALSE,2,15,TRUE,97,'CRITICAL','Cisco IOS XE implant campaign; disable HTTP/HTTPS server.',NOW()-INTERVAL '22 hours'),
('CVE-2024-23897',0.88,0.996,TRUE,FALSE,4,30,TRUE,92,'CRITICAL','Jenkins file read to RCE; patch and rotate secrets exposed via CLI.',NOW()-INTERVAL '26 hours'),
('CVE-2023-22515',0.88,0.996,TRUE,FALSE,2,14,TRUE,95,'CRITICAL','Confluence create-admin exploited in the wild; patch Data Center/Server.',NOW()-INTERVAL '30 hours'),
('CVE-2022-26134',0.955,0.998,TRUE,FALSE,6,40,TRUE,95,'CRITICAL','Confluence OGNL unauth RCE; a favourite of cryptomining and ransomware crews.',NOW()-INTERVAL '34 hours'),
('CVE-2021-26855',0.955,0.998,TRUE,FALSE,7,55,TRUE,94,'CRITICAL','ProxyLogon SSRF chained to RCE; hunt for webshells on Exchange.',NOW()-INTERVAL '38 hours'),
('CVE-2022-41040',0.90,0.997,TRUE,FALSE,3,22,TRUE,82,'CRITICAL','ProxyNotShell SSRF; apply mitigations and patches on Exchange.',NOW()-INTERVAL '42 hours'),
('CVE-2022-41082',0.90,0.997,TRUE,FALSE,3,22,TRUE,82,'CRITICAL','ProxyNotShell RCE; requires authenticated user plus SSRF.',NOW()-INTERVAL '46 hours'),
('CVE-2020-1472',0.955,0.999,TRUE,TRUE,9,70,TRUE,96,'CRITICAL','Zerologon instant DA takeover; ensure August 2020+ patches and enforcement mode.',NOW()-INTERVAL '50 hours'),
('CVE-2021-34527',0.88,0.996,TRUE,FALSE,8,50,TRUE,86,'CRITICAL','PrintNightmare SYSTEM RCE; patch and harden Point-and-Print.',NOW()-INTERVAL '54 hours'),
('CVE-2022-30190',0.90,0.997,TRUE,FALSE,6,40,TRUE,78,'HIGH','Follina Office RCE without macros; apply MSDT workaround/patch.',NOW()-INTERVAL '58 hours'),
('CVE-2023-27997',0.88,0.996,TRUE,FALSE,3,20,TRUE,94,'CRITICAL','FortiOS SSL-VPN pre-auth RCE; patch and monitor VPN logs.',NOW()-INTERVAL '62 hours'),
('CVE-2022-42475',0.90,0.997,TRUE,FALSE,2,16,TRUE,94,'CRITICAL','FortiOS heap overflow exploited in the wild; patch and hunt for IOCs.',NOW()-INTERVAL '66 hours'),
('CVE-2024-21887',0.92,0.998,TRUE,FALSE,4,28,TRUE,93,'CRITICAL','Ivanti command injection; assume compromise and rebuild affected appliances.',NOW()-INTERVAL '70 hours'),
('CVE-2023-46805',0.90,0.997,TRUE,FALSE,4,26,TRUE,80,'CRITICAL','Ivanti auth bypass; chained with 2024-21887 for unauth RCE.',NOW()-INTERVAL '74 hours'),
('CVE-2024-27198',0.90,0.997,TRUE,FALSE,3,24,TRUE,92,'CRITICAL','TeamCity auth bypass; protects CI/CD supply chain — patch now.',NOW()-INTERVAL '78 hours'),
('CVE-2023-3519',0.90,0.997,TRUE,FALSE,3,20,TRUE,93,'CRITICAL','Citrix ADC zero-day RCE; hunt for webshells and rotate secrets.',NOW()-INTERVAL '82 hours'),
('CVE-2021-21972',0.90,0.997,TRUE,FALSE,7,45,TRUE,90,'CRITICAL','vCenter unauth RCE; restrict vSphere Client access and patch.',NOW()-INTERVAL '88 hours'),
('CVE-2019-0708',0.90,0.998,TRUE,FALSE,10,60,TRUE,90,'CRITICAL','BlueKeep wormable RDP RCE; patch and enable NLA.',NOW()-INTERVAL '96 hours'),
('CVE-2017-0144',0.94,0.999,TRUE,TRUE,15,80,TRUE,88,'CRITICAL','EternalBlue SMBv1 RCE; disable SMBv1 everywhere.',NOW()-INTERVAL '104 hours'),
('CVE-2024-6387',0.36,0.93,FALSE,FALSE,3,40,TRUE,66,'HIGH','regreSSHion unauth root RCE; difficult but impactful — patch OpenSSH.',NOW()-INTERVAL '110 hours'),
('CVE-2022-3602',0.10,0.85,FALSE,FALSE,1,8,TRUE,68,'HIGH','OpenSSL 3.0 punycode overflow; patch to 3.0.7 (impact lower than first feared).',NOW()-INTERVAL '118 hours'),
('CVE-2023-44487',0.80,0.99,TRUE,FALSE,4,50,TRUE,74,'HIGH','HTTP/2 Rapid Reset DDoS; apply vendor mitigations across the web tier.',NOW()-INTERVAL '126 hours'),
('CVE-2024-3094',0.28,0.92,FALSE,FALSE,2,30,TRUE,84,'CRITICAL','XZ backdoor supply-chain near-miss; verify liblzma versions on all hosts.',NOW()-INTERVAL '134 hours'),
('CVE-2023-50164',0.88,0.996,FALSE,FALSE,3,22,TRUE,86,'CRITICAL','Apache Struts file-upload RCE; patch and review upload handling.',NOW()-INTERVAL '140 hours'),
('CVE-2021-4034',0.50,0.95,TRUE,FALSE,12,70,TRUE,72,'HIGH','PwnKit local root on nearly all Linux; patch polkit promptly.',NOW()-INTERVAL '150 hours'),
('CVE-2022-0847',0.42,0.94,FALSE,FALSE,8,55,TRUE,70,'HIGH','Dirty Pipe local root on Linux 5.8+; patch kernel.',NOW()-INTERVAL '158 hours'),
('CVE-2023-38831',0.85,0.995,TRUE,FALSE,5,35,TRUE,76,'HIGH','WinRAR archive RCE used by APTs; update WinRAR.',NOW()-INTERVAL '164 hours'),
('CVE-2024-25600',0.90,0.997,TRUE,FALSE,3,26,TRUE,93,'CRITICAL','WordPress Bricks Builder unauth RCE actively exploited; update immediately.',NOW()-INTERVAL '15 hours');

-- --- Lab inventory -----------------------------------------------------------
INSERT INTO lab_assets (name, note, added_by) VALUES
('apache','Reverse proxy + web tier','demo'),
('log4j','Java logging in the app stack','demo'),
('openssl','TLS across services','demo'),
('vmware','vCenter / ESXi lab','demo'),
('exchange','Mail server (test domain)','demo'),
('fortinet','Perimeter SSL-VPN','demo'),
('wordpress','Marketing site','demo'),
('citrix','Remote access gateway','demo')
ON CONFLICT (name) DO NOTHING;

-- --- Tickets (auto-raised: fused CVE hitting a lab asset) ---------------------
INSERT INTO tickets (cve_id, assets, priority, status, checklist, created_at) VALUES
('CVE-2021-44228','{log4j}',100,'open',
 '1. Inventory all Log4j2 versions across services.\n2. Upgrade to Log4j 2.17.1+ (or remove JndiLookup class).\n3. Block outbound LDAP/RMI at the egress firewall.\n4. Hunt logs for ${jndi: patterns.\n5. Rotate any credentials exposed in JNDI callbacks.',
 NOW()-INTERVAL '3 hours'),
('CVE-2023-4966','{citrix}',97,'open',
 '1. Patch NetScaler ADC/Gateway to a fixed build.\n2. Terminate ALL active sessions (patching alone is insufficient).\n3. Review for session-hijack indicators.\n4. Rotate credentials used over the gateway.',
 NOW()-INTERVAL '14 hours'),
('CVE-2022-3602','{openssl}',68,'open',
 '1. Identify OpenSSL 3.0.x deployments.\n2. Upgrade to OpenSSL 3.0.7.\n3. Restart dependent services.\n4. Confirm no static links to vulnerable liblzma/OpenSSL.',
 NOW()-INTERVAL '118 hours');

INSERT INTO tickets (cve_id, assets, priority, status, checklist, created_at, closed_at) VALUES
('CVE-2021-26855','{exchange}',94,'closed','Applied Exchange SU, hunted for webshells (clean), rotated service accounts.',NOW()-INTERVAL '38 hours',NOW()-INTERVAL '30 hours'),
('CVE-2023-27997','{fortinet}',94,'closed','Patched FortiOS, reviewed VPN logs, no IOCs found.',NOW()-INTERVAL '62 hours',NOW()-INTERVAL '55 hours');

-- --- Intelligence reports (agent crew) ---------------------------------------
INSERT INTO reports (title, summary, content, created_at) VALUES
('Executive Intelligence Report — Weekly Threat Landscape',
 'This week saw sustained mass-exploitation of edge and remote-access devices. Citrix Bleed (CVE-2023-4966) and ConnectWise ScreenConnect (CVE-2024-1709) remain the highest-signal threats, both actively exploited by ransomware affiliates. Your lab exposure is concentrated in three assets (log4j, citrix, openssl) with open remediation tickets. Overall posture is B-grade: known exposures are tracked and in-flight, with no unmanaged critical gaps. Priority this week: complete the Citrix session-invalidation step, which patching alone does not resolve.',
 'THREAT LEVEL: HIGH\n\nCRITICAL FINDINGS\n- CVE-2024-3400 (PAN-OS) and CVE-2024-1709 (ScreenConnect) are unauth RCE, exploited as zero-days.\n- Citrix Bleed requires session invalidation, not just patching.\n\nAFFECTED ASSETS\n- log4j, apache: Log4Shell family (ticket open, P100)\n- citrix: Citrix Bleed (ticket open, P97)\n- openssl: X.509 punycode overflow (ticket open, P68)\n\nRECOMMENDATIONS\n1. Close the Citrix ticket by invalidating all active NetScaler sessions.\n2. Maintain egress filtering to blunt Log4j-style callbacks.\n3. Continue weekly KEV review; 24 of the tracked CVEs are on the CISA KEV list.',
 NOW()-INTERVAL '12 hours'),
('Technical Deep-Dive — Edge Device Exploitation Trends',
 'A technical review of the quarter''s most-exploited vulnerability classes: authentication bypasses in remote-access gateways (Citrix, Ivanti, ScreenConnect, TeamCity) and pre-auth memory-safety bugs in VPN appliances (FortiOS). EPSS scores for these CVEs cluster above 0.90, and all appear on CISA KEV. Detection guidance and MITRE ATT&CK mappings included.',
 'IOC & DETECTION\n- Watch for anomalous admin-account creation (T1136) on Confluence, ScreenConnect, Cisco IOS XE.\n- Monitor SSL-VPN appliances for crash/restart loops (exploit attempts).\n\nMITRE ATT&CK\n- Initial Access: T1190 Exploit Public-Facing Application\n- Persistence: T1505.003 Web Shell\n- Priv-Esc: T1068 Exploitation for Privilege Escalation\n\nREMEDIATION PRIORITY\nRank by CCC priority: PAN-OS 99 > MOVEit 98 > ScreenConnect 98 > Citrix Bleed 97 = Spring4Shell 97.',
 NOW()-INTERVAL '40 hours');

-- --- Learning (practice journal + HTB owns) ----------------------------------
INSERT INTO practice_log (username, machine, platform, skills, difficulty, notes, source, practiced_at) VALUES
('demo','Manager','HTB','{"active directory","kerberos","mssql"}','Hard','ADCS ESC1 to DA via certificate abuse.','manual',NOW()-INTERVAL '2 days'),
('demo','Codify','HTB','{"nodejs","vm2 sandbox escape","password cracking"}','Easy','vm2 sandbox escape then sudo misconfig.','manual',NOW()-INTERVAL '4 days'),
('demo','Authority','HTB','{"active directory","adcs","pwm"}','Medium','PWM creds to ADCS ESC1.','manual',NOW()-INTERVAL '6 days'),
('demo','Sau','HTB','{"ssrf","request-baskets","systemctl"}','Easy','SSRF via request-baskets to internal Maltrail RCE.','manual',NOW()-INTERVAL '9 days'),
('demo','Devvortex','HTB','{"joomla","cve exploitation","apport"}','Easy','Joomla API leak to admin RCE, apport-cli priv-esc.','manual',NOW()-INTERVAL '12 days'),
('demo','Analytics','HTB','{"metabase","cve exploitation","ubuntu overlayfs"}','Easy','Metabase pre-auth RCE, GameOverlay priv-esc.','manual',NOW()-INTERVAL '15 days');

INSERT INTO htb_machines (machine_id, name, os, difficulty, points, retired, skill_areas, user_owned, root_owned) VALUES
(1,'Manager','Windows','Hard',40,TRUE,'{"active directory","adcs"}',TRUE,TRUE),
(2,'Codify','Linux','Easy',20,TRUE,'{"nodejs","sandbox escape"}',TRUE,TRUE),
(3,'Authority','Windows','Medium',30,TRUE,'{"active directory","adcs"}',TRUE,TRUE),
(4,'Sau','Linux','Easy',20,TRUE,'{"ssrf","rce"}',TRUE,TRUE),
(5,'Devvortex','Linux','Easy',20,TRUE,'{"joomla","priv-esc"}',TRUE,TRUE),
(6,'Analytics','Linux','Easy',20,TRUE,'{"metabase","overlayfs"}',TRUE,TRUE),
(7,'Monitored','Linux','Medium',30,TRUE,'{"nagios","snmp"}',TRUE,FALSE),
(8,'Corporate','Linux','Insane',50,FALSE,'{"saml","xss"}',FALSE,FALSE);

-- --- Knowledge base (docs + chunks; embeddings are placeholders) --------------
INSERT INTO kb_documents (title, source_type, source_ref, content_hash, added_by, chunk_count) VALUES
('Incident Response Runbook','pdf','ir-runbook.pdf','demo-hash-ir-001','demo',3),
('Log4Shell Mitigation Notes','note','log4shell.md','demo-hash-log4j-002','demo',2),
('Active Directory Hardening Checklist','pdf','ad-hardening.pdf','demo-hash-ad-003','demo',3),
('SOC Alert Triage Playbook','note','triage.md','demo-hash-triage-004','demo',2);

INSERT INTO kb_chunks (document_id, chunk_index, content, embedding) VALUES
(1,0,'Incident response phases: preparation, identification, containment, eradication, recovery, lessons learned.','{0.01,0.02,0.03,0.04}'),
(1,1,'Containment: isolate affected hosts, preserve volatile memory, capture network flows before remediation.','{0.02,0.03,0.04,0.05}'),
(1,2,'Recovery: restore from known-good backups, rotate all potentially exposed credentials, monitor for reinfection.','{0.03,0.04,0.05,0.06}'),
(2,0,'Log4Shell: upgrade to Log4j 2.17.1+, remove the JndiLookup class, and block outbound LDAP/RMI at egress.','{0.04,0.05,0.06,0.07}'),
(2,1,'Detection: grep application logs for ${jndi: and monitor for anomalous outbound LDAP connections.','{0.05,0.06,0.07,0.08}'),
(3,0,'AD hardening: enforce SMB signing, disable NTLMv1, tier administrative accounts, and monitor Kerberoasting.','{0.06,0.07,0.08,0.09}'),
(3,1,'ADCS: audit certificate templates for ESC1-ESC8 misconfigurations that allow domain escalation.','{0.07,0.08,0.09,0.10}'),
(3,2,'Enforce Zerologon (CVE-2020-1472) enforcement mode and monitor Netlogon secure-channel events.','{0.08,0.09,0.10,0.11}'),
(4,0,'Triage: correlate alerts with asset criticality and threat intel before escalating to an incident.','{0.09,0.10,0.11,0.12}'),
(4,1,'Prioritise alerts touching internet-facing assets on the CISA KEV list within the last 24 hours.','{0.10,0.11,0.12,0.13}');

-- --- News feed ---------------------------------------------------------------
-- Links point at canonical, always-live references (NVD CVE pages + the CISA KEV
-- catalog) so demo headlines never 404. `source` is the outlet that covered it.
INSERT INTO news_articles (title, url, source, description, published_date, created_at) VALUES
('CISA adds actively exploited edge-device flaws to KEV catalog','https://www.cisa.gov/known-exploited-vulnerabilities-catalog','CISA','New known-exploited vulnerabilities added, urging federal agencies to patch within the due date.',NOW()-INTERVAL '4 hours',NOW()-INTERVAL '4 hours'),
('Ransomware affiliates exploit Citrix Bleed to breach enterprises','https://nvd.nist.gov/vuln/detail/CVE-2023-4966','BleepingComputer','Multiple ransomware groups leverage CVE-2023-4966 for initial access and session hijacking.',NOW()-INTERVAL '10 hours',NOW()-INTERVAL '10 hours'),
('New OpenSSH regreSSHion flaw enables unauthenticated root RCE','https://nvd.nist.gov/vuln/detail/CVE-2024-6387','The Hacker News','CVE-2024-6387 affects glibc Linux systems; exploitation is difficult but demonstrated.',NOW()-INTERVAL '16 hours',NOW()-INTERVAL '16 hours'),
('Mass exploitation of ConnectWise ScreenConnect underway','https://nvd.nist.gov/vuln/detail/CVE-2024-1709','BleepingComputer','Attackers exploit CVE-2024-1709 to deploy ransomware and infostealers on unpatched servers.',NOW()-INTERVAL '21 hours',NOW()-INTERVAL '21 hours'),
('XZ Utils backdoor: how a supply-chain attack nearly hit millions','https://nvd.nist.gov/vuln/detail/CVE-2024-3094','Ars Technica','Analysis of the malicious liblzma code that would have backdoored sshd across major distros.',NOW()-INTERVAL '30 hours',NOW()-INTERVAL '30 hours'),
('Palo Alto patches PAN-OS zero-day exploited in the wild','https://nvd.nist.gov/vuln/detail/CVE-2024-3400','The Hacker News','CVE-2024-3400 allows unauthenticated root command execution on GlobalProtect gateways.',NOW()-INTERVAL '44 hours',NOW()-INTERVAL '44 hours'),
('HTTP/2 Rapid Reset drives record-breaking DDoS attacks','https://nvd.nist.gov/vuln/detail/CVE-2023-44487','Cloudflare','CVE-2023-44487 abused for the largest DDoS attacks observed to date.',NOW()-INTERVAL '60 hours',NOW()-INTERVAL '60 hours'),
('JetBrains TeamCity auth bypass threatens CI/CD supply chains','https://nvd.nist.gov/vuln/detail/CVE-2024-27198','The Hacker News','CVE-2024-27198 lets unauthenticated attackers seize control of build pipelines.',NOW()-INTERVAL '76 hours',NOW()-INTERVAL '76 hours');

-- --- Activity (monitors, commands, AI, analyst) ------------------------------
INSERT INTO monitor_runs (task, started, finished, status, items_found, items_posted, last_success) VALUES
('cve',NOW()-INTERVAL '58 minutes',NOW()-INTERVAL '57 minutes','success',6,4,NOW()-INTERVAL '57 minutes'),
('news',NOW()-INTERVAL '118 minutes',NOW()-INTERVAL '117 minutes','success',8,8,NOW()-INTERVAL '117 minutes'),
('cve',NOW()-INTERVAL '2 hours',NOW()-INTERVAL '119 minutes','success',5,3,NOW()-INTERVAL '119 minutes'),
('htb',NOW()-INTERVAL '20 hours',NOW()-INTERVAL '20 hours','success',8,0,NOW()-INTERVAL '20 hours');

INSERT INTO ai_metrics (kind, model, elapsed_ms, cache_hit, created_at) VALUES
('summary','qwen2.5:3b',6400,FALSE,NOW()-INTERVAL '3 hours'),
('summary','qwen2.5:3b',180,TRUE,NOW()-INTERVAL '5 hours'),
('enrichment','qwen2.5:3b',7100,FALSE,NOW()-INTERVAL '11 hours'),
('report','qwen2.5:3b',48000,FALSE,NOW()-INTERVAL '12 hours'),
('analyst','qwen2.5:3b',6900,FALSE,NOW()-INTERVAL '1 hour');

INSERT INTO command_logs (user_id, username, command, created_at) VALUES
(1,'demo','/analyst',NOW()-INTERVAL '20 minutes'),
(1,'demo','/cve',NOW()-INTERVAL '55 minutes'),
(1,'demo','/tickets',NOW()-INTERVAL '90 minutes'),
(1,'demo','/analyst',NOW()-INTERVAL '3 hours'),
(1,'demo','/brief',NOW()-INTERVAL '5 hours'),
(1,'demo','/report',NOW()-INTERVAL '12 hours'),
(1,'demo','/lab',NOW()-INTERVAL '13 hours'),
(1,'demo','/status',NOW()-INTERVAL '14 hours'),
(1,'demo','/news',NOW()-INTERVAL '16 hours'),
(1,'demo','/analyst',NOW()-INTERVAL '18 hours'),
(1,'demo','/recommend',NOW()-INTERVAL '22 hours'),
(1,'demo','/kb-search',NOW()-INTERVAL '26 hours');

INSERT INTO analyst_log (user_id, username, query, intent, tools, sources, used_llm, elapsed_ms, created_at) VALUES
(1,'demo','what should I patch today?','PATCH_PRIORITIES','{cves.top,cves.kev,assets.affected,tickets.open}','{"CVE Database","CISA KEV","Asset Inventory"}',FALSE,6,NOW()-INTERVAL '20 minutes'),
(1,'demo','does my lab have any exposure?','AFFECTED_ASSETS','{assets.affected}','{"Asset Inventory","CVE Database"}',FALSE,9,NOW()-INTERVAL '3 hours'),
(1,'demo','explain CVE-2021-44228','EXPLAIN_CVE','{cves.get,assets.by_cve,rag.search}','{"CVE Database","Asset Inventory","RAG Knowledge Base"}',TRUE,7200,NOW()-INTERVAL '5 hours'),
(1,'demo','summarise overnight threats','OVERNIGHT','{cves.counts,cves.top,cves.kev,news.recent}','{"CVE Database","CISA KEV","RSS News"}',FALSE,14,NOW()-INTERVAL '9 hours'),
(1,'demo','what is a reverse shell?','EXPLAIN_TOPIC','{rag.search}','{"RAG Knowledge Base","LLM"}',TRUE,8100,NOW()-INTERVAL '18 hours');

INSERT INTO audit_log (actor, action, target, source, created_at) VALUES
('demo','lab.add','log4j','discord',NOW()-INTERVAL '13 hours'),
('demo','ticket.close','CVE-2021-26855','discord',NOW()-INTERVAL '30 hours'),
('admin','auth.login','dashboard','dashboard',NOW()-INTERVAL '1 hour');
