import os
import glob
import re

template_dir = 'd:/website/templates'
html_files = glob.glob(os.path.join(template_dir, '*.html'))

for file in html_files:
    if os.path.basename(file) in ['dmca-validation.html', 'login.html', 'register.html']:
        continue
        
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
    
    # 1. Update Nạp tiền href to /nap-tien
    content = content.replace('href="/recharge"', 'href="/nap-tien"')
    
    # 2. Update Kiếm tiền icon
    content = re.sub(r'<i class="fa-solid [^"]+"></i>(\s*<span>Kiếm tiền</span>)', r'<i class="fa-solid fa-money-bills"></i>\g<1>', content)
    
    # 3. Add DMCA badge to sidebar-footer
    if 'dmca-badge-container' not in content:
        # find sidebar-footer and insert
        dmca_code = '''
        <!-- Badge DMCA -->
        <div
          class="dmca-badge-container"
          style="text-align: center; margin-top: 15px"
        >
          <a
            href="//www.dmca.com/Protection/Status.aspx?ID=7f567101-2b8a-44f2-9d65-7f71f3677539"
            title="DMCA.com Protection Status"
            class="dmca-badge"
          >
            <img
              src="https://images.dmca.com/Badges/dmca_protected_sml_120ae.png?ID=7f567101-2b8a-44f2-9d65-7f71f3677539"
              alt="DMCA.com Protection Status"
          /></a>
          <script src="https://images.dmca.com/Badges/DMCABadgeHelper.min.js"></script>
        </div>'''
        
        # Replace the closing of sidebar-footer
        content = re.sub(r'(<button class="btn-logout" id="btnLogout">[\s\S]*?</button>\s*)</div>', r'\1' + dmca_code + '\n      </div>', content)
        
    if content != original:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {os.path.basename(file)}')
