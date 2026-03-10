import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";
import { Shield } from "lucide-react";

export function OTPVerifyPage() {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [resending, setResending] = useState(false);
  const { verifyOtp, sendOtp, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleVerify = async () => {
    if (code.length !== 6) return;
    setError("");
    try {
      await verifyOtp(code);
      navigate("/dashboard");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Verification failed";
      setError(msg);
    }
  };

  const handleResend = async () => {
    setResending(true);
    try {
      await sendOtp("email");
    } catch {
      setError("Failed to resend OTP");
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-sand px-6">
      <Card className="w-full max-w-sm border-border/50">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <Shield className="h-10 w-10 text-desert-gold" />
          </div>
          <CardTitle className="text-2xl">Verify your email</CardTitle>
          <CardDescription>Enter the 6-digit code sent to your email</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="rounded-lg bg-sunset-red/10 border border-sunset-red/20 px-4 py-3 text-sm text-sunset-red">
              {error}
            </div>
          )}
          <div className="flex justify-center">
            <InputOTP maxLength={6} value={code} onChange={setCode}>
              <InputOTPGroup>
                <InputOTPSlot index={0} />
                <InputOTPSlot index={1} />
                <InputOTPSlot index={2} />
                <InputOTPSlot index={3} />
                <InputOTPSlot index={4} />
                <InputOTPSlot index={5} />
              </InputOTPGroup>
            </InputOTP>
          </div>
          <Button
            onClick={handleVerify}
            className="w-full bg-oasis-teal hover:bg-oasis-teal/90 text-white"
            disabled={code.length !== 6 || isLoading}
          >
            {isLoading ? "Verifying..." : "Verify"}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            Didn't receive the code?{" "}
            <button onClick={handleResend} disabled={resending} className="text-oasis-teal font-medium hover:underline">
              {resending ? "Sending..." : "Resend"}
            </button>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
