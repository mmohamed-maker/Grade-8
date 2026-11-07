export function validateIdentity(p, audience) {
  if (!p || !audience || p.aud !== audience ||
      !['accounts.google.com','https://accounts.google.com'].includes(p.iss) ||
      p.email_verified !== true || p.hd !== 'ikns.edu.bh' ||
      !p.sub || !p.email || !p.email.toLowerCase().endsWith('@ikns.edu.bh') ||
      !Number.isFinite(p.exp) || p.exp * 1000 <= Date.now()) {
    throw new Error('ACCESS_DENIED');
  }
  return {email:p.email.toLowerCase(), sub:p.sub};
}
export function validateRequest(b) {
  if (!b || !['status','start'].includes(b.action) ||
      typeof b.assessment !== 'string' || b.assessment.length > 80)
    throw new Error('INVALID_REQUEST');
  if (b.action === 'start' && !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(b.requestId || ''))
    throw new Error('INVALID_REQUEST');
  return b;
}
