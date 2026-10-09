import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const code=fs.readFileSync(new URL('../public/app.js',import.meta.url),'utf8');
const m=code.match(/function overlaps\(a,b\)\{[^}]*\}/);
assert.ok(m,'Frontend must keep one overlaps function');
const overlaps=vm.runInNewContext('('+m[0]+')');
test('Frontend Integral spans morning+afternoon, not night',()=>{
 for(const [a,b,expected] of [
  ['Integral','Manhã',true],['Manhã','Integral',true],
  ['Integral','Tarde',true],['Tarde','Integral',true],
  ['Integral','Noite',false],['Noite','Integral',false],
  ['Manhã','Noite',false],['Tarde','Noite',false],
  ['Manhã','Tarde',false],['Noite','Noite',true],
  ['Integral','Integral',true],['Outro','Noite',true]
 ])assert.equal(overlaps(a,b),expected,a+' / '+b);
});
