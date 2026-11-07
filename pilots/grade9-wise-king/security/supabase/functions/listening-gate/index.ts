import { OAuth2Client } from 'npm:google-auth-library@9';
import { createClient } from 'npm:@supabase/supabase-js@2';
import { validateIdentity, validateRequest } from './policy.mjs';

// Set secrets in Supabase; NEVER commit service-role credentials.
const audience = Deno.env.get('GOOGLE_CLIENT_ID') || '';
const origin = Deno.env.get('ALLOWED_ORIGIN') || '';
const google = new OAuth2Client(audience);
const admin = createClient(Deno.env.get('SUPABASE_URL')!,
 Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);
const headers = {
 'Access-Control-Allow-Origin':origin,
 'Access-Control-Allow-Headers':'authorization, content-type',
 'Access-Control-Allow-Methods':'POST, OPTIONS',
 'Cache-Control':'no-store',
 'Content-Type':'application/json',
 'Vary':'Origin'
};
Deno.serve(async (req) => {
 const reply = (data:unknown,status=200) => new Response(JSON.stringify(data),{status,headers});
 if (!origin || req.headers.get('origin') !== origin || !audience)
   return reply({error:'ACCESS_DENIED'},403);
 if (req.method==='OPTIONS') return new Response(null,{status:204,headers});
 if (req.method!=='POST') return reply({error:'METHOD_NOT_ALLOWED'},405);
 try {
   const token = req.headers.get('authorization')?.match(/^Bearer (.+)$/)?.[1];
   if (!token || token.length>10000) return reply({error:'ACCESS_DENIED'},401);
   // Cryptographically verify issuer, audience, expiration and signature first.
   const ticket = await google.verifyIdToken({idToken:token,audience});
   const person = validateIdentity(ticket.getPayload(),audience);
   const raw = await req.text();
   if (raw.length>2048) return reply({error:'INVALID_REQUEST'},400);
   const b = validateRequest(JSON.parse(raw));
   const {data,error} = await admin.rpc('listening_gate',{
     p_assessment:b.assessment,p_email:person.email,p_sub:person.sub,
     p_action:b.action,p_request:b.action==='start'?b.requestId:null
   });
   if (error) {
     const allowed=['OUTSIDE_WINDOW','LIMIT_REACHED','PLAYBACK_ACTIVE',
       'INSUFFICIENT_TIME','REQUEST_EXPIRED'];
     return reply({error:allowed.find(c=>error.message.includes(c)) || 'ACCESS_DENIED'},403);
   }
   if (b.action==='status') return reply(data);
   const ttl=Math.floor((Date.parse(data.expiresAt)-Date.now())/1000);
   if(ttl<1) return reply({error:'REQUEST_EXPIRED'},403);
   const signed = await admin.storage.from('listening-private')
     .createSignedUrl(data.path,Math.min(ttl,60));
   if(signed.error) return reply({error:'MEDIA_UNAVAILABLE'},503);
   const {path,...safe}=data;
   return reply({...safe,audioUrl:signed.data.signedUrl});
 } catch {
   return reply({error:'ACCESS_DENIED'},403);
 }
});
