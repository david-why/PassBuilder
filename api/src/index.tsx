import { Hono } from 'hono'
import * as pkijs from 'pkijs'
import * as asn1js from 'asn1js'
import { pemToBuffer } from './utils/crypto'

interface HonoEnv {
  Bindings: Env
}

const app = new Hono<HonoEnv>()

app.get('/', (c) => {
  return c.text('Hello, Hono!')
})

app.post('/sign', async (c) => {
  const text = await c.req.arrayBuffer()
  if (!text) {
    return c.json({ error: 'Signature body is required' }, 400)
  }
  const textBuffer = text

  try {
    // Load private and public keys
    const privateKeyDer = pemToBuffer(c.env.PASSKIT_PRIVATE_KEY)
    const privateKey = await crypto.subtle.importKey(
      'pkcs8',
      privateKeyDer,
      { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-1' },
      true,
      ['sign']
    )
    const cert = pkijs.Certificate.fromBER(
      pemToBuffer(c.env.PASSKIT_CERTIFICATE)
    )
    const wwdr = pkijs.Certificate.fromBER(pemToBuffer(c.env.APPLE_WWDR_CERT))

    // Create SignerInfo
    const messageDigest = await crypto.subtle.digest("SHA-1", textBuffer);
    console.log('Message digest hex:', new Uint8Array(messageDigest));
    const signerInfo = new pkijs.SignerInfo({
      // version: 1,
      sid: new pkijs.IssuerAndSerialNumber({
        issuer: cert.issuer,
        serialNumber: cert.serialNumber,
      }),
      signedAttrs: new pkijs.SignedAndUnsignedAttributes({
        type: 0,
        attributes: [
          new pkijs.Attribute({
            type: '1.2.840.113549.1.9.3', // content-type
            values: [
              new asn1js.ObjectIdentifier({ value: '1.2.840.113549.1.7.1' }), // id-data
            ],
          }),
          new pkijs.Attribute({
            type: '1.2.840.113549.1.9.4', // message-digest
            values: [
              // The value will be filled in automatically by pkijs during signing
              new asn1js.OctetString({ valueHex: messageDigest }),
            ],
          }),
          new pkijs.Attribute({
            type: '1.2.840.113549.1.9.5', // signingTime
            values: [new asn1js.UTCTime({ valueDate: new Date() })],
          }),
        ],
      }),
    })

    // Create detached SignedData (no eContent for detached signature)
    const signed = new pkijs.SignedData({
      // version: 1,
      encapContentInfo: new pkijs.EncapsulatedContentInfo({
        eContentType: '1.2.840.113549.1.7.1', // id-data
        // No eContent for detached signature
      }),
      signerInfos: [signerInfo],
      certificates: [cert, wwdr],
    })

    // Sign with detached data
    await signed.sign(privateKey, 0, 'SHA-1', textBuffer)

    // Create ContentInfo wrapper for detached signature
    const contentInfo = new pkijs.ContentInfo({
      contentType: '1.2.840.113549.1.7.2', // signedData
      content: signed.toSchema(true),
    })

    const signatureBytes = contentInfo.toSchema().toBER()
    console.log('Detached signature created successfully')

    return c.json({
      success: true,
      signature: Array.from(new Uint8Array(signatureBytes)),
      signatureBase64: btoa(
        String.fromCharCode(...new Uint8Array(signatureBytes))
      ),
    })
  } catch (error) {
    console.error('Signing error:', error)
    return c.json({ error: 'Failed to sign data' }, 500)
  }
})

export default app
