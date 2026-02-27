'use client';

import { useEffect, useState } from 'react';
import { fetchWithAuth } from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function KidDashboard({ profile: initialProfile }: { profile: any }) {
    const router = useRouter();
    const [chores, setChores] = useState([]);
    const [rewards, setRewards] = useState([]);
    const [profile, setProfile] = useState(initialProfile);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadDashboard = async () => {
            try {
                const [choresRes, rewardsRes] = await Promise.all([
                    fetchWithAuth('/chores/'),
                    fetchWithAuth('/rewards/')
                ]);
                setChores(await choresRes.json());
                setRewards(await rewardsRes.json());
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        loadDashboard();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.push('/login');
    };

    const completeChore = async (id: number) => {
        try {
            const res = await fetchWithAuth(`/chores/${id}/complete/`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                setChores(chores.filter((c: any) => c.id !== id));
                setProfile({ ...profile, points: data.new_points });
            }
        } catch (e) { }
    };

    const redeemReward = async (id: number) => {
        try {
            const res = await fetchWithAuth(`/rewards/${id}/redeem/`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                setProfile({ ...profile, points: data.new_points });
                alert("Reward redeemed! Waiting for parent approval.");
            } else {
                alert("Not enough points!");
            }
        } catch (e) { }
    };

    if (loading) return null;

    return (
        <div className="space-y-12 pb-24 max-w-5xl mx-auto p-4 md:p-8">
            {/* Top Navbar */}
            <nav className="bg-white/80 backdrop-blur-md border border-gray-200 px-4 py-3 dark:bg-gray-900/80 dark:border-gray-800 rounded-full flex justify-between items-center shadow-sm sticky top-4 z-50 transition-all duration-300">
                <div className="flex items-center gap-3">
                    <img className="w-10 h-10 rounded-full border-2 border-primary object-cover"
                        src={`https://ui-avatars.com/api/?name=${profile.user.first_name || profile.user.username}&background=2DD4BF&color=fff`}
                        alt="Child Avatar" />
                    <span className="text-lg font-bold text-gray-800 dark:text-gray-100 hidden sm:inline-block">
                        Hi, {profile.user.first_name || profile.user.username}!
                    </span>
                </div>
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={handleLogout} className="text-gray-400 hover:text-red-500 rounded-full">
                        <LogOut className="h-5 w-5" />
                    </Button>
                </div>
            </nav>

            {/* Hero Section */}
            <div className="relative bg-gradient-to-br from-amber-400 to-orange-500 rounded-[2rem] p-8 md:p-12 mb-10 overflow-hidden shadow-lg shadow-amber-500/30 transform hover:scale-[1.01] transition-transform duration-300">
                <div className="absolute top-0 right-0 -mt-10 -mr-10 w-48 h-48 bg-white opacity-20 rounded-full blur-2xl"></div>
                <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-32 h-32 bg-white opacity-20 rounded-full blur-xl"></div>

                <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="text-center md:text-left text-white">
                        <h1 className="text-3xl md:text-4xl font-extrabold drop-shadow-sm mb-2">You're doing great! 🚀</h1>
                        <p className="text-yellow-100 font-medium opacity-90">Complete tasks to save up for big rewards.</p>
                    </div>

                    <div className="bg-white/20 backdrop-blur-md rounded-3xl p-6 px-10 border border-white/30 text-center shadow-inner">
                        <span className="block text-yellow-100 font-bold uppercase tracking-widest text-xs mb-1">Current Balance</span>
                        <div className="flex items-baseline justify-center gap-2">
                            <span className="text-6xl font-black text-white drop-shadow-md tracking-tight">{profile.points}</span>
                            <span className="text-lg font-bold text-yellow-50 drop-shadow-sm uppercase">pts</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                {/* Tasks Section */}
                <div className="space-y-6">
                    <h2 className="text-2xl font-black tracking-tight text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="p-2 bg-teal-400/20 rounded-lg text-teal-500">📝</span>
                        Your Tasks Today
                    </h2>

                    {chores.length > 0 ? (
                        <div className="space-y-4">
                            {chores.map((chore: any) => (
                                <div key={chore.id} className="group relative bg-white dark:bg-gray-800 rounded-2xl shadow-sm hover:shadow-md border border-gray-100 dark:border-gray-700 p-5 pl-6 transition-all duration-300 hover:-translate-y-1 flex justify-between items-center overflow-hidden">
                                    <div className="absolute left-0 top-0 bottom-0 w-2 bg-teal-400 rounded-l-2xl"></div>

                                    <div className="flex items-center gap-5">
                                        <div className="w-14 h-14 bg-teal-400/10 rounded-full flex justify-center items-center text-3xl shrink-0 group-hover:scale-110 transition-transform">
                                            {chore.icon || "📝"}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 group-hover:text-teal-500 transition-colors">
                                                {chore.title}
                                            </h3>
                                            <span className="inline-block mt-1 bg-yellow-100 text-yellow-800 text-xs font-bold px-2 py-0.5 rounded">
                                                {chore.points_value} pts
                                            </span>
                                        </div>
                                    </div>

                                    <Button
                                        onClick={() => completeChore(chore.id)}
                                        className="bg-teal-400 hover:bg-teal-500 text-white font-bold h-12 w-12 rounded-xl flex items-center justify-center shadow-md shadow-teal-400/40 active:scale-95 transition-all">
                                        <Check className="w-6 h-6" strokeWidth={3} />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="bg-white dark:bg-gray-800 rounded-2xl p-10 flex flex-col items-center text-center shadow-sm border border-gray-100 h-64 justify-center relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-amber-400/5 to-teal-400/5"></div>
                            <div className="text-5xl mb-4 animate-bounce relative z-10">🎉</div>
                            <h3 className="text-xl font-bold text-gray-800 dark:text-white relative z-10">All done!</h3>
                            <p className="text-gray-500 mt-2 font-medium relative z-10">You have no more tasks left for today.</p>
                        </div>
                    )}
                </div>

                {/* Rewards Section */}
                <div className="space-y-6">
                    <h2 className="text-2xl font-black tracking-tight text-gray-800 dark:text-white flex items-center gap-2">
                        <span className="p-2 bg-amber-400/20 rounded-lg text-amber-500">🎁</span>
                        Rewards Store
                    </h2>

                    <div className="grid grid-cols-2 gap-4">
                        {rewards.map((reward: any) => {
                            const canAfford = profile.points >= reward.cost;
                            return (
                                <div key={reward.id} className={`group bg-gradient-to-br from-white to-orange-50/50 dark:from-gray-800 dark:to-gray-800 rounded-2xl shadow-sm border-2 ${canAfford ? 'border-amber-400/30 hover:border-amber-400 hover:shadow-lg' : 'border-gray-100 grayscale-[0.8] opacity-80'} transition-all p-5 flex flex-col items-center text-center relative overflow-hidden`}>
                                    <div className="w-16 h-16 bg-amber-400/10 rounded-full flex justify-center items-center text-4xl mb-4 group-hover:-translate-y-2 transition-transform drop-shadow-sm">
                                        {reward.icon || "🎁"}
                                    </div>
                                    <h3 className="font-bold text-gray-800 dark:text-white leading-tight mb-1">{reward.title}</h3>
                                    <p className="text-sm font-black text-amber-500 mb-5">{reward.cost} pts</p>

                                    <div className="w-full mt-auto relative z-10">
                                        {canAfford ? (
                                            <Button onClick={() => redeemReward(reward.id)} className="w-full rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold shadow-md shadow-amber-500/40 hover:-translate-y-0.5 transition-all">
                                                Get Reward
                                            </Button>
                                        ) : (
                                            <div className="w-full py-2 bg-gray-100 dark:bg-gray-700 text-gray-500 text-sm font-bold rounded-xl border cursor-not-allowed">
                                                Need {reward.cost - profile.points} more
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}
