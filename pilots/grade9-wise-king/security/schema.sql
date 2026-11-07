-- Run once in Supabase SQL editor as project administrator.
-- No real roster, schedule, transcript or answer key is stored in this repository.
create schema if not exists listening_private;
revoke all on schema listening_private from public, anon, authenticated;
create table listening_private.assessments (
 id text primary key,
 enabled boolean not null default false,
 opens_at timestamptz,
 closes_at timestamptz,
 audio_path text,
 audio_seconds integer check (audio_seconds > 0),
 check (closes_at > opens_at)
);
create table listening_private.roster (
 assessment_id text references listening_private.assessments(id),
 email text check (email = lower(email) and split_part(email,'@',2) = 'ikns.edu.bh'),
 google_sub text,
 used integer not null default 0 check (used between 0 and 3),
 active_until timestamptz,
 primary key(assessment_id,email),
 unique(assessment_id,google_sub)
);
create table listening_private.plays (
 assessment_id text not null,
 email text not null,
 request_id uuid not null,
 issued_at timestamptz not null,
 expires_at timestamptz not null,
 primary key(assessment_id,email,request_id),
 foreign key(assessment_id,email) references listening_private.roster(assessment_id,email)
);
alter table listening_private.assessments enable row level security;
alter table listening_private.roster enable row level security;
alter table listening_private.plays enable row level security;
revoke all on all tables in schema listening_private from public, anon, authenticated;
insert into listening_private.assessments(id) values ('grade9-wise-king');

-- Only trusted server calls this function, AFTER verifying Google's signed ID token.
create or replace function public.listening_gate(
 p_assessment text, p_email text, p_sub text, p_action text, p_request uuid default null
) returns jsonb
language plpgsql security definer set search_path = ''
as $$
declare
 a listening_private.assessments%rowtype;
 r listening_private.roster%rowtype;
 previous listening_private.plays%rowtype;
 t timestamptz;
 until_time timestamptz;
begin
 if p_action not in ('status','start') or p_sub is null or p_sub = '' then
   raise exception 'ACCESS_DENIED';
 end if;
 select * into a from listening_private.assessments where id=p_assessment for share;
 if not found or not a.enabled or a.opens_at is null or a.closes_at is null
   or a.audio_path is null or a.audio_seconds is null then
   raise exception 'ACCESS_DENIED';
 end if;
 select * into r from listening_private.roster
   where assessment_id=p_assessment and email=p_email for update;
 if not found then raise exception 'ACCESS_DENIED'; end if;
 -- Use server wall-clock after acquiring locks; browser clock is never trusted.
 t := clock_timestamp();
 if t < a.opens_at or t >= a.closes_at then raise exception 'OUTSIDE_WINDOW'; end if;
 if r.google_sub is not null and r.google_sub <> p_sub then
   raise exception 'ACCESS_DENIED';
 end if;
 if r.google_sub is null then
   update listening_private.roster set google_sub=p_sub
    where assessment_id=p_assessment and email=p_email;
 end if;
 if p_action='status' then
   return jsonb_build_object('remaining',3-r.used,'closesAt',a.closes_at,
     'activeUntil',r.active_until,'serverTime',t);
 end if;
 if p_request is null then raise exception 'INVALID_REQUEST'; end if;
 select * into previous from listening_private.plays
  where assessment_id=p_assessment and email=p_email and request_id=p_request;
 if found then
   -- Idempotent retries never consume another attempt or extend media access.
   if t >= previous.expires_at then raise exception 'REQUEST_EXPIRED'; end if;
   return jsonb_build_object('remaining',3-r.used,'path',a.audio_path,
    'expiresAt',previous.expires_at,'activeUntil',r.active_until,'closesAt',a.closes_at);
 end if;
 if r.used >= 3 then raise exception 'LIMIT_REACHED'; end if;
 if r.active_until > t then raise exception 'PLAYBACK_ACTIVE'; end if;
 -- Refuse a new play unless enough assessment time remains for the whole audio.
 if t + make_interval(secs=>a.audio_seconds+5) > a.closes_at then
   raise exception 'INSUFFICIENT_TIME';
 end if;
 until_time := t + make_interval(secs=>a.audio_seconds+5);
 update listening_private.roster set used=used+1,active_until=until_time
  where assessment_id=p_assessment and email=p_email;
 insert into listening_private.plays values
  (p_assessment,p_email,p_request,t,least(t+interval '60 seconds',a.closes_at));
 return jsonb_build_object('remaining',2-r.used,'path',a.audio_path,
  'expiresAt',least(t+interval '60 seconds',a.closes_at),
  'activeUntil',until_time,'closesAt',a.closes_at);
end;
$$;
revoke all on function public.listening_gate(text,text,text,text,uuid) from public,anon,authenticated;
grant execute on function public.listening_gate(text,text,text,text,uuid) to service_role;
