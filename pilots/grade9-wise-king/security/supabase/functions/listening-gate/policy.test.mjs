import test from 'node:test';
import assert from 'node:assert/strict';
import {validateIdentity,validateRequest} from './policy.mjs';
const base={aud:'client',iss:'https://accounts.google.com',email_verified:true,
 hd:'ikns.edu.bh',sub:'google-sub',email:'1234567@ikns.edu.bh',exp:Math.floor(Date.now()/1000)+3600};
test('valid verified school identity',()=>assert.equal(validateIdentity(base,'client').sub,'google-sub'));
for (const [label,patch] of [
 ['other domain',{hd:'gmail.com'}],['suffix attack',{email:'x@ikns.edu.bh.evil.test'}],
 ['unverified',{email_verified:false}],['wrong audience',{aud:'other'}],
 ['wrong issuer',{iss:'https://evil.test'}],['expired',{exp:1}],['missing hosted domain',{hd:undefined}],
 ['missing subject',{sub:''}]]) {
 test(label,()=>assert.throws(()=>validateIdentity({...base,...patch},'client')));
}
test('missing configuration denied',()=>assert.throws(()=>validateIdentity(base,'')));
test('start requires UUID retry key',()=>assert.throws(()=>validateRequest({action:'start',assessment:'grade9-wise-king'})));
test('valid start',()=>assert.equal(validateRequest({action:'start',assessment:'grade9-wise-king',requestId:'12345678-1234-4123-8123-123456789abc'}).action,'start'));
test('unsupported actions denied',()=>assert.throws(()=>validateRequest({action:'reset',assessment:'grade9-wise-king'})));
