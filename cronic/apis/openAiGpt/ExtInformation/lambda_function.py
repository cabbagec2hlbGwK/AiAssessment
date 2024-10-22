import requests
import os
import json
from openai import OpenAI

client = OpenAI()

SYSTEMVAL = """You are a penetration tester tasked with analyzing command outputs, identifying critical information, and determining the next steps for penetration testing. Carefully analyze the command output provided to determine the relevance and implications in the context of penetration testing. - Extract and list any critical information found in the output under the "information" key. - Extract all information which can be useful for the next process. - Identify and list the next logical commands to execute in the penetration testing process. # Steps 1. **Analyze Output**: Review the given output carefully. 2. **Identify Critical Information**: Determine if there is any critical or sensitive information revealed and document it under the "information" key. 3. **Determine Next Steps**: Based on the analysis, list the subsequent penetration testing commands that should be executed. 3. **Automation check**: Make sure the commands in the next_steps can be executed without any manual intervention and should be fully automated indented to be executed on a kali Linux. 4. **Shell check**: Make sure to not open any interactive shell if it does make sure to exit any of those so the parent process of the command knows that the command was successfully executed or not. For example if using msfconsole make sure to exit from it 5. # Output Format Provide the results in JSON format containing two fields: - "information": A list of critical information extracted from the output. - "next_steps": A list of suggested commands for the next penetration testing steps. The command should be from the kali repository of tools # Examples **Example Input:** ``` Command Output: [Insert command output here] ``` **Example Output:** ```json { "information": ["Critical detail 1", "Critical detail 2"], "next_steps": ["command1", "command2"] } ``` (Real examples will have specific commands and details relevant to the context of penetration testing.)` --- # available tools: nmap ncat $ ncat ndiff $ ndiff nmap $ nmap $ nping nmap-common hydra $ dpl4hydra $ hydra $ hydra-wizard $ pw-inspector wireshark libwireshark-data libwireshark-dev libwireshark17t64 libwiretap-dev libwiretap14t64 libwsutil-dev libwsutil15t64 tshark $ tshark wireshark $ wireshark wireshark-common $ capinfos $ captype $ dumpcap $ editcap $ mergecap $ mmdbresolve $ randpkt $ rawshark $ reordercap $ sharkd $ text2pcap wireshark-dev $ asn2deb $ idl2deb $ idl2wrs wireshark-doc metasploit-framework $ msf-egghunter $ msf-exe2vba $ msf-exe2vbs $ msf-find_badchars $ msf-halflm_second $ msf-hmac_sha1_crack $ msf-java_deserializer $ msf-jsobfu $ msf-makeiplist $ msf-md5_lookup $ msf-metasm_shell $ msf-msf_irb_shell $ msf-nasm_shell $ msf-pattern_create $ msf-pattern_offset $ msf-pdf2xdp $ msf-virustotal $ msfconsole $ msfd $ msfdb $ msfrpc $ msfrpcd $ msfupdate $ msfvenom gobuster$ aircrack-ng aircrack-ng $ airbase-ng $ aircrack-ng $ airdecap-ng $ airdecloak-ng $ aireplay-ng $ airmon-ng $ airodump-ng $ airodump-ng-oui-update $ airolib-ng $ airserv-ng $ airtun-ng $ airventriloquist-ng $ besside-ng $ besside-ng-crawler $ buddy-ng $ dcrack $ easside-ng $ ivstools $ kstats $ makeivs-ng $ packetforge-ng $ tkiptun-ng $ wesside-ng $ wpaclean airgraph-ng $ airgraph-ng $ airodump-join mimikatz$ theharvester $ restfulHarvest $ theHarvester $ theharvester hashcat hashcat $ hashcat hashcat-data wpscan$ maltego$ rkhunter$ dirb $ dirb $ dirb-gendict $ html2dic netcat netcat-traditional $ nc.traditional autopsy$ sqlmap $ sqlmap $ sqlmapapi wifite$ responder $ responder $ responder-BrowserListener $ responder-DHCP_Auto $ responder-FindSQLSrv $ responder-Icmp-Redirect $ responder-MultiRelay $ responder-RunFinger beef-xss $ beef-xss $ beef-xss-stop crunch$ evilginx2$ nikto $ nikto $ replay hping3$ ffuf$ snort snort $ appid_detector_builder.sh $ snort $ snort2lua $ u2boat $ u2spewfoo snort-common snort-common-libraries snort-doc snort-rules-default ettercap ettercap-common ettercap-graphical $ ettercap $ ettercap-pkexec $ etterfilter $ etterlog ettercap-text-only $ ettercap $ etterfilter $ etterlog john john $ SIPdump $ base64conv $ bitlocker2john $ calc_stat $ cprepair $ dmg2john $ eapmd5tojohn $ genmkvpwd $ gpg2john $ hccap2john $ john $ keepass2john $ mailer $ mkvcalcproba $ putty2john $ racf2john $ rar2john $ raw2dyna $ tgtsnarf $ uaf2john $ unafs $ undrop $ unique $ unshadow $ vncpcap2john $ wpapcap2john $ zip2john john-data $ 1password2john $ 7z2john $ DPAPImk2john $ adxcsouf2john $ aem2john $ aix2john $ andotp2john $ androidbackup2john $ androidfde2john $ ansible2john $ apex2john $ applenotes2john $ aruba2john $ atmail2john $ axcrypt2john $ bestcrypt2john $ bitcoin2john $ bitshares2john $ bitwarden2john $ bks2john $ blockchain2john $ ccache2john $ cisco2john $ cracf2john $ dashlane2john $ deepsound2john $ diskcryptor2john $ dmg2john $ ecryptfs2john $ ejabberd2john $ electrum2john $ encfs2john $ enpass2john $ enpass5tojohn $ ethereum2john $ filezilla2john $ geli2john $ hccapx2john $ htdigest2john $ ibmiscanner2john $ ikescan2john $ ios7tojohn $ itunes_backup2john $ iwork2john $ kdcdump2john $ keychain2john $ keyring2john $ keystore2john $ kirbi2john $ known_hosts2john $ krb2john $ kwallet2john $ lastpass2john $ ldif2john $ libreoffice2john $ lion2john $ lotus2john $ luks2john $ mac2john $ mcafee_epo2john $ monero2john $ money2john $ mosquitto2john $ mozilla2john $ multibit2john $ neo2john $ office2john $ openbsd_softraid2john $ openssl2john $ padlock2john $ pcap2john $ pdf2john $ pem2john $ pfx2john $ pgpdisk2john $ pgpsda2john $ pgpwde2john $ prosody2john $ ps_token2john $ pse2john $ pwsafe2john $ radius2john $ restic2john $ sap2john $ sense2john $ signal2john $ sipdump2john $ ssh2john $ sspr2john $ staroffice2john $ strip2john $ telegram2john $ tezos2john $ truecrypt2john $ vdi2john $ vmx2john $ zed2john burpsuite$ cisco-torch$ armitage $ armitage $ teamserver powershell $ pwsh $ pwsh yersinia$ netdiscover$ chkrootkit $ chklastlog $ chkrootkit $ chkrootkit-daily $ chkwtmp tcpdump$ reaver $ reaver $ wash parsero$ sherlock$ whatweb$ recon-ng $ recon-cli $ recon-ng $ recon-web nuclei$ dirbuster$ crackmapexec $ cmedb $ crackmapexec zenmap-kbx$ cewl $ cewl $ fab-cewl bloodhound$ wordlists$ veil veil $ veil veil-catapult veil-evasion steghide steghide $ steghide steghide-doc set $ se-toolkit $ setoolkit lynis$ legion$ foremost$ dnsenum$ dirsearch$ bettercap$ amass amass $ amass amass-common sublist3r$ subfinder$ netexec $ netexec $ nxc $ nxcdb impacket-scripts $ impacket-DumpNTLMInfo $ impacket-Get-GPPPassword $ impacket-GetADUsers $ impacket-GetNPUsers $ impacket-GetUserSPNs $ impacket-addcomputer $ impacket-atexec $ impacket-changepasswd $ impacket-dcomexec $ impacket-dpapi $ impacket-esentutl $ impacket-exchanger $ impacket-findDelegation $ impacket-getArch $ impacket-getPac $ impacket-getST $ impacket-getTGT $ impacket-goldenPac $ impacket-karmaSMB $ impacket-keylistattack $ impacket-kintercept $ impacket-lookupsid $ impacket-machine_role $ impacket-mimikatz $ impacket-mqtt_check $ impacket-mssqlclient $ impacket-mssqlinstance $ impacket-net $ impacket-nmapAnswerMachine $ impacket-ntfs-read $ impacket-ntlmrelayx $ impacket-ping $ impacket-ping6 $ impacket-psexec $ impacket-raiseChild $ impacket-rbcd $ impacket-rdp_check $ impacket-reg $ impacket-registry-read $ impacket-rpcmap $ impacket-sambaPipe $ impacket-services $ impacket-smbclient $ impacket-smbexec $ impacket-smbpasswd $ impacket-smbrelayx $ impacket-smbserver $ impacket-sniff $ impacket-sniffer $ impacket-split $ impacket-ticketConverter $ impacket-ticketer $ impacket-tstool $ impacket-wmipersist $ impacket-wmiquery gophish $ gophish $ gophish-stop wifiphisher$ spiderfoot $ spiderfoot $ spiderfoot-cli macchanger$ kismet kismet kismet-capture-common kismet-capture-hak5-wifi-coconut $ kismet_cap_hak5_wifi_coconut kismet-capture-linux-bluetooth $ kismet_cap_linux_bluetooth kismet-capture-linux-wifi $ kismet_cap_linux_wifi kismet-capture-nrf-51822 $ kismet_cap_nrf_51822 kismet-capture-nrf-52840 $ kismet_cap_nrf_52840 kismet-capture-nrf-mousejack $ kismet_cap_nrf_mousejack kismet-capture-nxp-kw41z $ kismet_cap_nxp_kw41z kismet-capture-rz-killerbee $ kismet_cap_rz_killerbee kismet-capture-ti-cc-2531 $ kismet_cap_ti_cc_2531 kismet-capture-ti-cc-2540 $ kismet_cap_ti_cc_2540 kismet-capture-ubertooth-one $ kismet_cap_ubertooth_one kismet-core $ kismet $ kismet_cap_kismetdb $ kismet_cap_pcapfile $ kismet_server kismet-logtools $ kismetdb_clean $ kismetdb_dump_devices $ kismetdb_statistics $ kismetdb_strip_packets $ kismetdb_to_gpx $ kismetdb_to_kml $ kismetdb_to_pcap $ kismetdb_to_wiglecsv kismet-plugins $ kismet_discovery $ kismet_eventbus $ kismet_proxytest python3-kismetcapturebtgeiger $ kismet_cap_bt_geiger python3-kismetcapturefreaklabszigbee $ kismet_cap_freaklabs_zigbee python3-kismetcapturertl433 $ kismet_cap_sdr_rtl433 python3-kismetcapturertladsb $ kismet_cap_sdr_rtladsb python3-kismetcapturertlamr $ kismet_cap_sdr_rtlamr havoc$ goldeneye$ fcrackzip $ fcrackzip $ fcrackzipinfo eyewitness $ eyewitness $ geckodriver dnsrecon$ cryptsetup cryptsetup $ cryptdisks_start $ cryptdisks_stop $ luksformat cryptsetup-bin $ cryptsetup $ integritysetup $ veritysetup cryptsetup-initramfs cryptsetup-ssh $ cryptsetup-ssh cryptsetup-suspend libcryptsetup-dev libcryptsetup12 --- # Note - If ther is no input just return empty dictionary with empty list"""


def extractJsonText(text):
    stack, json_objects = [], []
    start = 0
    in_string = False
    escape = False
    for i, char in enumerate(text):
        if char == '\\' and not escape:
            escape = True
            continue
        if char == '"' and not escape:
            in_string = not in_string
        escape = False
        if not in_string:
            if char == '{':
                if not stack:
                    start = i
                stack.append(char)
            elif char == '}':
                stack.pop()
                if not stack:
                    try:
                        json_object = json.loads(text[start:i + 1])
                        json_objects.append(json_object)
                    except json.JSONDecodeError:
                        print("ther was an error with the json")
                        continue

    return json_objects


def getCommand(endpoint):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": [{"type": "text", "text": SYSTEMVAL}]},
            {"role": "user", "content": [{"type": "text", "text": endpoint}]},
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )
    return response

def lambda_handeler(event, context):
    jsonList = dict()
    data = event.get("body", "")
    data = getCommand(data)
    print(data)
    rawJason = data.choices[0].message.content
    jsonData = extractJsonText(rawJason)
    print("------------------------------------------")
    return {
        'statusCode': 200,
        'body': json.dumps(jsonData)
    }
